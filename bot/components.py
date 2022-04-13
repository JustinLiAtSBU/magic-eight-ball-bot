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
    async def upvote(self, button, interaction):
        self.votes[interaction.user] = 1
        if self.all_voted():
            for child in self.children:
                child.disabled = re.match(self.pattern, child.custom_id)
            await self.ctx.send(embed=self.votes_embed())
            await interaction.response.edit_message(view=self)

    @discord.ui.button(custom_id='downvote_button', style=discord.ButtonStyle.danger, emoji="👎")
    async def downvote(self, button, interaction):
        self.votes[interaction.user] = -1
        if self.all_voted():
            for child in self.children:
                child.disabled = re.match(self.pattern, child.custom_id)
            await self.ctx.send(embed=self.votes_embed())
            await interaction.response.edit_message(view=self)

    # TODO: Add watched feature for users in upcoming release
    # @discord.ui.button(label="Watched", style=discord.ButtonStyle.blurple, emoji="👀")
    # async def watched(self, button, interaction):
    #     await interaction.response.send_message("Watched")

    def all_voted(self):
        return len([vote for vote in self.votes.values() if vote != 0]) == len(self.members)

    def votes_result(self):
        result = {
            'total': sum([vote for vote in self.votes.values() if vote != 0]),
            'upvotes': len([vote for vote in self.votes.values() if vote == 1]),
            'downvotes': len([vote for vote in self.votes.values() if vote == -1])
        }
        return result

    def votes_embed(self):
        result = self.votes_result()
        embed_color = 0x808080
        result_value = "TIE\n"
        if result['total'] > 0:
            result_value = "WATCH ▶️ \n"
            embed_color = 0x00ff00
        elif result['total'] < 0:
            result_value = "SKIP ⏭\n"
            embed_color = 0xff0000

        embed = discord.Embed(title=f"🗳  Votes are in for **{self.data['title']}**", description="", color=embed_color)
        embed.add_field(name="Result", value=result_value, inline=True)
        embed.add_field(name="Upvotes", value=f"{result['upvotes']} ⬆️ ", inline=False)
        embed.add_field(name="Downvotes", value=f"{result['downvotes']} ⬇️ ", inline=False)
        return embed