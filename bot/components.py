from discord.ui import Button, View
import discord


class UpVoteButton(Button):
    def __init__(self):
        super().__init__(label="", style=discord.ButtonStyle.blurple, emoji="👍")

    async def callback(self, interaction):
        print(interaction)
        await interaction.response.send_message("Hi")