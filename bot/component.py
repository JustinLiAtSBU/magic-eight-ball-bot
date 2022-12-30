import discord
from seasoning import progress_bar
from discord.ui import View
from requester import *


class Ballot(View):
    def __init__(self, ctx, request, data, members, callback, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.request = request
        self.data = data
        self.members = members
        self.callback = callback
        self.votes = {member: 0 for member in members}
        self.dont_suggest_votes = {member: 0 for member in members}
        self.pattern = r"(.*)vote_button"

    @discord.ui.button(custom_id='upvote_button', style=discord.ButtonStyle.green, emoji="👍")
    async def upvote_callback(self, interaction, button):
        self.votes[interaction.user] = 1
        self.update_button_votes()
        if self.all_voted():
            self.disable_vote_buttons()
            self.get_dont_suggest_button().label = "Watched "
            await self.ctx.send(embed=self.votes_embed())
        await interaction.response.edit_message(view=self)

    @discord.ui.button(custom_id='downvote_button', style=discord.ButtonStyle.danger, emoji="👎")
    async def downvote_callback(self, interaction, button):
        self.votes[interaction.user] = -1
        self.update_button_votes()
        if self.all_voted():
            self.disable_vote_buttons()
            await self.ctx.send(embed=self.votes_embed())
            await self.callback
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Don't Suggest 🚫 ", custom_id='dont_suggest_button', style=discord.ButtonStyle.blurple)
    async def dont_suggest_callback(self, interaction, button):
        self.dont_suggest_votes[interaction.user] = 1
        ratio = self.update_dont_suggest_button(button)
        if ratio >= 0.5:
            self.disable_dont_suggest_button()
            if self.get_upvote_button().disabled is False:
                await self.callback
            self.disable_vote_buttons()
            if 'movie' in self.request['type']:
                await update_channels_watched_movies(self.ctx.channel.id, self.data)
            else:
                await update_channels_watched_tv_shows(self.ctx.channel.id, self.data)
            await self.ctx.send(f"Added **{self.data['title']}** to channels **Don't Suggest List**")
        await interaction.response.edit_message(view=self)

    def all_voted(self):
        return len([vote for vote in self.votes.values() if vote != 0]) == len(self.members)

    def total_votes(self):
        return sum([vote for vote in self.votes.values() if vote != 0])

    def upvotes(self):
        return len([vote for vote in self.votes.values() if vote == 1])

    def downvotes(self):
        return len([vote for vote in self.votes.values() if vote == -1])

    def total_dont_suggest_votes(self):
        return len([vote for vote in self.dont_suggest_votes.values() if vote == 1])

    def update_dont_suggest_button(self, button):
        ratio = self.total_dont_suggest_votes() / len(self.members)
        progress = progress_bar(self.total_dont_suggest_votes(), len(self.members), length=10)
        button.label += progress
        return ratio

    def update_button_votes(self):
        for child in self.children:
            if child.custom_id == 'upvote_button':
                child.label = f"{self.upvotes()}" if self.upvotes() > 0 else ''
            elif child.custom_id == 'downvote_button':
                child.label = f"{self.downvotes()}" if self.downvotes() > 0 else ''

    def disable_vote_buttons(self):
        self.get_upvote_button().disabled = True
        self.get_downvote_button().disabled = True

    def disable_dont_suggest_button(self):
        self.get_dont_suggest_button().disabled = True

    def get_upvote_button(self):
        for child in self.children:
            if child.custom_id is not None and child.custom_id == 'upvote_button':
                return child

    def get_downvote_button(self):
        for child in self.children:
            if child.custom_id is not None and child.custom_id == 'downvote_button':
                return child

    def get_dont_suggest_button(self):
        for child in self.children:
            if child.custom_id is not None and child.custom_id == 'dont_suggest_button':
                return child

    def votes_embed(self):
        embed_color = 0x808080
        result_value = "TIE\n"
        if self.total_votes() > 0:
            result_value = "WATCH ▶️ \n"
            embed_color = 0x00ff00
        elif self.total_votes() < 0:
            result_value = "SKIP ⏭\n"
            embed_color = 0xff0000

        embed = discord.Embed(title=f"🗳  Votes are in for **{self.data['title']}**", description="", color=embed_color)
        embed.add_field(name="Result", value=result_value, inline=True)
        embed.add_field(name="Upvotes", value=f"{self.upvotes()} ⬆️ ", inline=False)
        embed.add_field(name="Downvotes", value=f"{self.downvotes()} ⬇️ ", inline=False)
        return embed
