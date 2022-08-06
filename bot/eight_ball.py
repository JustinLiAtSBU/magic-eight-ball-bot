import os
import re
import random
import discord
from typing import Final
from dotenv import load_dotenv
from discord.ext import commands
from seasoning import progress_bar
from discord.ui import Button, View
from component import Ballot
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
        
        if 'anime' in request['type']:
            url = f"https://animixplay.to/?q={'%20'.join(data['title'].split(' '))}"
        else:
            url = f"https://ww5.0123movie.net/search/{'+'.join(data['title'].split(' '))}.html"
        watch_link = Button(label="Watch Free", style=discord.ButtonStyle.blurple, url=url, emoji="🏴‍☠️")
        view.add_item(watch_link)
        
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


bot.run(TOKEN)