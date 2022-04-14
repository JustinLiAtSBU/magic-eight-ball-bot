import discord
import re
from discord.ui import Button, View

class Ballot(View):
    def __init__(self, ctx, data, members, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.data = data
        self.members = members
        self.votes = { member : 0 for member in members}
        self.pattern = r"(.*)vote_button"

    @discord.ui.button(custom_id='upvote_button', style=discord.ButtonStyle.green, emoji="👍")
    async def upvote_callback(self, button, interaction):
        self.votes[interaction.user] = 1
        if self.all_voted():
            self.disable_vote_buttons()
            await self.ctx.send(embed=self.votes_embed())
        else:
            self.update_button_votes()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(custom_id='downvote_button', style=discord.ButtonStyle.danger, emoji="👎")
    async def downvote_callback(self, button, interaction):
        self.votes[interaction.user] = -1
        if self.all_voted():
            self.disable_vote_buttons()
            await self.ctx.send(embed=self.votes_embed())
        else:
            self.update_button_votes()
        await interaction.response.edit_message(view=self)

    # TODO: Add watched feature for users in upcoming release
    # @discord.ui.button(label="Watched", style=discord.ButtonStyle.blurple, emoji="👀")
    # async def watched_callback(self, button, interaction):
    #     await interaction.response.send_message("Watched")

    def all_voted(self):
        return len([vote for vote in self.votes.values() if vote != 0]) == len(self.members)

    def total_votes(self):
        return sum([vote for vote in self.votes.values() if vote != 0])

    def upvotes(self):
        return len([vote for vote in self.votes.values() if vote == 1])

    def downvotes(self):
        return len([vote for vote in self.votes.values() if vote == -1])
    
    def update_button_votes(self):
        for child in self.children:
            if child.custom_id == 'upvote_button':
                child.label = f"{self.upvotes()}" if self.upvotes() > 0 else ''
            elif child.custom_id == 'downvote_button':
                child.label = f"{self.downvotes()}" if self.downvotes() > 0 else ''
    
    def disable_vote_buttons(self):
        for child in self.children:
            child.disabled = re.match(self.pattern, child.custom_id)

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