import os
import re
import random
import discord
from typing import Final
# from components import Ballot
from dotenv import load_dotenv
from discord.ext import commands
from seasoning import progress_bar
from discord.ui import Button, View
from seasoning import get_name, user_request_response, motion_picture_embed
from requester import *



load_dotenv()
TOKEN: Final = os.getenv('DISCORD_TOKEN')
intents = discord.Intents().default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')

@bot.command(name='whoisstreaming', help='Tells you who is going to stream')
async def who_streaming(ctx):
    await create_or_update_channel(ctx)
    members = get_online_channel_members(ctx)
    streamer = random.choice(members)
    await ctx.send(f"You're streaming {get_name(streamer)}")

@bot.command(name='randommovie', help='Gives you a random movie to watch.')
async def random_movie(ctx, *args):
    request = {
        'type': 'movie',
        'top': 100
    }
    await send_message_with_data(ctx, request, args, random_movie(ctx, *args))

@bot.command(name='randomtvshow', help='Gives you a random TV show to watch.')
async def random_tv_show(ctx, *args):
    request = {
        'type': 'TV show',
        'top': 100
    }
    await send_message_with_data(ctx, request, args, random_tv_show(ctx, *args))

@bot.command(name='randomanime', help='Gives you a random anime to watch.')
async def random_anime(ctx):
    args = ('country=JP', 'genres=animation')
    request = {
        'type': 'anime',
        'top': 1000,
        'country': 'Japan',
        'genres': 'animation'
    }
    await send_message_with_data(ctx, request, args, random_anime(ctx))

@bot.command(name='randomanimemovie', help='Gives you a random anime movie to watch.')
async def random_anime_movie(ctx):
    args = ('country=JP', 'genres=animation')
    request = {
        'type': 'anime movie',
        'top': 1000,
        'country': 'Japan',
        'genres': 'animation'
    }
    await send_message_with_data(ctx, request, args, random_anime_movie(ctx))

async def send_message_with_data(ctx, request, args, callback):
    await create_or_update_channel(ctx)
    await ctx.send(user_request_response(ctx.author, request, args))
    data = await random_motion_picture_request(ctx.channel.id, request, args)
    if data is None:
        await ctx.send(f"No {request['type']}s found with those criteria")
    else:
        view = Ballot(ctx, request, data, get_online_channel_members(ctx), callback, timeout=600)
        # TODO: Figure out how to make animix links 100% accurate
        if 'anime' in request['type']:
            url =  "https://animixplay.to/v1/" + '-'.join(data['title'].split(' '))
            animix_link = Button(label="Watch Free", style=discord.ButtonStyle.blurple, url=url, emoji="<a:kannaWink:909791444661850132>")
            view.add_item(animix_link)
        if request['type'] == 'movie' or request['type'] == 'TV show':
            imdb_button = Button(label="IMDB", style=discord.ButtonStyle.link, url=f"https://www.imdb.com/title/{data['tconst']}")
            view.add_item(imdb_button)

        await ctx.send(embed=motion_picture_embed(ctx.author, data), view=view)

def get_online_channel_members(ctx):
    return [f"{m.name}#{m.discriminator}" for m in ctx.channel.members if not m.bot and m.status is discord.Status.online]

def get_all_channel_members(ctx):
    return [f"{m.name}#{m.discriminator}" for m in ctx.channel.members if not m.bot]

async def create_or_update_channel(ctx):
    params = {
        'channelId': str(ctx.channel.id),
        'channelName': ctx.channel.name,
        'guild': ctx.guild.name
    }
    body = get_all_channel_members(ctx)
    await create_channel_request(params, body)


class Ballot(View):
    def __init__(self, ctx, request, data, members, callback, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.request = request
        self.data = data
        self.members = members
        self.callback = callback
        self.votes = { member : 0 for member in members}
        self.dont_suggest_votes = { member : 0 for member in members}
        self.pattern = r"(.*)vote_button"

    @discord.ui.button(custom_id='upvote_button', style=discord.ButtonStyle.green, emoji="👍")
    async def upvote_callback(self, button, interaction):
        self.votes[interaction.user] = 1
        self.update_button_votes()
        if self.all_voted():
            self.disable_vote_buttons()
            await self.ctx.send(embed=self.votes_embed())
        await interaction.response.edit_message(view=self)

    @discord.ui.button(custom_id='downvote_button', style=discord.ButtonStyle.danger, emoji="👎")
    async def downvote_callback(self, button, interaction):
        self.votes[interaction.user] = -1
        self.update_button_votes()
        if self.all_voted():
            self.disable_vote_buttons()
            await self.ctx.send(embed=self.votes_embed())
            await self.callback
        await interaction.response.edit_message(view=self)

    # TODO: Add watched feature for users in upcoming release
    @discord.ui.button(label="Don't Suggest Again 🚫 ", custom_id='dont_suggest_button', style=discord.ButtonStyle.blurple)
    async def dont_suggest_callback(self, button, interaction):
        self.dont_suggest_votes[interaction.user] = 1
        ratio = self.update_dont_suggest_button(button)
        if ratio >= 0.5:
            self.disable_dont_suggest_button()
            if 'movie' in self.request['type']:
                await update_channels_watched_movies(self.ctx.channel.id, self.data)
            else:
                await update_channels_watched_tv_shows(self.ctx.channel.id, self.data)
            await self.ctx.send(f"Added **{self.data['title']}** to channels **Don't Suggest List**")
            await self.callback
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
        ratio = self.total_dont_suggest_votes()/len(self.members)
        progress = progress_bar(self.total_dont_suggest_votes(), len(self.members), length=20)
        button.label = f"Don't Suggest Again 🚫 {progress}"
        return ratio
    
    def update_button_votes(self):
        for child in self.children:
            if child.custom_id == 'upvote_button':
                child.label = f"{self.upvotes()}" if self.upvotes() > 0 else ''
            elif child.custom_id == 'downvote_button':
                child.label = f"{self.downvotes()}" if self.downvotes() > 0 else ''
    
    def disable_vote_buttons(self):
        for child in self.children:
            if child.custom_id is not None:
                child.disabled = re.match(self.pattern, child.custom_id)
    
    def disable_dont_suggest_button(self):
        for child in self.children:
            if child.custom_id is not None and child.custom_id == 'dont_suggest_button':
                child.disabled = True

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


bot.run(TOKEN)