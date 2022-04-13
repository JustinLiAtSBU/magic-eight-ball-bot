from turtle import down
import discord
import re
from discord.ui import Button, View

class Ballot(View):
    def __init__(self, ctx, members, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.members = members
        self.votes = { member : 0 for member in members}
        self.pattern = r"(.*)vote_button"

    @discord.ui.button(custom_id='upvote_button', style=discord.ButtonStyle.green, emoji="👍")
    async def upvote(self, button, interaction):
        self.votes[interaction.user] = 1
        if self.all_voted():
            for child in self.children:
                child.disabled = re.match(self.pattern, child.custom_id)
            await self.ctx.send(self.votes_message())
            await interaction.response.edit_message(view=self)

    @discord.ui.button(custom_id='downvote_button', style=discord.ButtonStyle.danger, emoji="👎")
    async def downvote(self, button, interaction):
        self.votes[interaction.user] = -1
        if self.all_voted():
            for child in self.children:
                child.disabled = re.match(self.pattern, child.custom_id)
            await self.ctx.send(self.votes_message())
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
            'upvotes': len([vote for vote in self.votes.values() if vote != -1]),
            'downvotes': len([vote for vote in self.votes.values() if vote != 1])
        }
        return result

    def votes_message(self):
        result = self.votes_result()
        message = f"Result: "
        if result['total'] > 0:
            message += "WATCH\n"
        elif result['total'] < 0:
            message += "SKIP\n"
        else:
            message += "TIE\n"
        message += f"Upvotes:   {result['upvotes']} ✅ \n"
        message += f"Downvotes: {result['downvotes']} ❌ \n"
        return message