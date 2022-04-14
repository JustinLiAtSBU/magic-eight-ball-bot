import os
import discord
import random
from components import Ballot
from dotenv import load_dotenv
from discord.ext import commands
from seasoning import get_name, user_request_response, motion_picture_embed
from typing import Final
from discord.ui import Button, View
from requester import build_and_send_request


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
    members = [i for i in ctx.channel.members if i.bot is not True]
    streamer = random.choice(members)
    await ctx.send(f"You're streaming {get_name(streamer)}")

@bot.command(name='randommovie', help='Gives you a random movie to watch.')
async def random_movie(ctx, *args):
    request = {
        'type': 'movie',
        'size': 100
    }
    await send_message_with_data(ctx, request, args)

@bot.command(name='randomtvshow', help='Gives you a random TV show to watch.')
async def random_tv_show(ctx, *args):
    request = {
        'type': 'TV show',
        'size': 100
    }
    await send_message_with_data(ctx, request, args)

@bot.command(name='randomanime', help='Gives you a random anime to watch.')
async def random_anime(ctx):
    args = ('country=JP', 'genres=animation')
    request = {
        'type': 'anime',
        'size': 1000,
        'country': 'Japan',
        'genres': 'animation'
    }
    await send_message_with_data(ctx, request, args)

@bot.command(name='randomanimemovie', help='Gives you a random anime movie to watch.')
async def random_anime_movie(ctx):
    args = ('country=JP', 'genres=animation')
    request = {
        'type': 'anime movie',
        'size': 1000,
        'country': 'Japan',
        'genres': 'animation'
    }
    await send_message_with_data(ctx, request, args)

async def send_message_with_data(ctx, request, args):
    await ctx.send(user_request_response(ctx.author, request, args))
    data =  build_and_send_request(request, args)
    view = Ballot(ctx, data, get_online_channel_members(ctx))
    # TODO: Figure out how to make animix links 100% accurate
    if 'anime' in request['type']:
        url =  "https://animixplay.to/v1/" + '-'.join(data['title'].split(' '))
        animix_link = discord.ui.Button(label="Watch Free", style=discord.ButtonStyle.blurple, url=url, emoji="<a:kannaWink:909791444661850132>")
        view.add_item(animix_link)
    if request['type'] == 'movie' or request['type'] == 'TV show':
        imdb_button = discord.ui.Button(label="IMDB", style=discord.ButtonStyle.link, url=f"https://www.imdb.com/title/{data['tconst']}")
        view.add_item(imdb_button)
    await ctx.send(embed=motion_picture_embed(ctx.author, data), view=view)

def get_online_channel_members(ctx):
    return [f"{m.name}#{m.discriminator}" for m in ctx.channel.members if not m.bot and m.status is discord.Status.online]

bot.run(TOKEN)