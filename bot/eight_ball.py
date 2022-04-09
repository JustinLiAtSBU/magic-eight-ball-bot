import os
import discord
import flag
import pycountry
import random
import requests
from dotenv import load_dotenv
from discord.ext import commands
from personalize import get_name
from typing import Final
from fuzzy_match import genre_match

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API = os.getenv('MAGIC_EIGHT_BALL_API')
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)
NON_MIN_QUERY_PARAMS: Final = ['country', 'size', 'genres']

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
    URL = f'{API}/api/movies/random'
    request = {
        'type': 'movie',
        'size': 100
    }
    try:
        await ctx.send(user_request_response(ctx.author, request, args))
        res = requests.get(url=URL, params=build_params(args))
        data = res.json()
        await ctx.send(embed=motion_picture_embed(ctx.author, data))
    except requests.exceptions.RequestException as e:
        await ctx.send("No movies found with those criteria")

@bot.command(name='randomtvshow', help='Gives you a random TV show to watch.')
async def random_tv_show(ctx, *args):
    URL = f'{API}/api/tvshows/random'
    request = {
        'type': 'TV show',
        'size': 100
    }
    try:
        await ctx.send(user_request_response(ctx.author, request, args))
        res = requests.get(url=URL, params=build_params(args))
        data = res.json()
        await ctx.send(embed=motion_picture_embed(ctx.author, data))
    except requests.exceptions.RequestException as e:
        await ctx.send("No TV shows found with those criteria")

@bot.command(name='randomanime', help='Gives you a random anime to watch.')
async def random_anime(ctx):
    args = ('country=JP', 'genres=animation')
    URL = f'{API}/api/tvshows/random'
    request = {
        'type': 'anime',
        'size': 1000,
        'country': 'Japan',
        'genres': 'animation'
    }
    try:
        await ctx.send(user_request_response(ctx.author, request, args))
        res = requests.get(url=URL, params=build_params(args))
        data = res.json()
        await ctx.send(embed=motion_picture_embed(ctx.author, data))
    except requests.exceptions.RequestException as e:
        await ctx.send("No animes found with those criteria")


@bot.command(name='randomanimemovie', help='Gives you a random anime movie to watch.')
async def random_anime_movie(ctx):
    args = ('country=JP', 'genres=animation')
    URL = f'{API}/api/movies/random'
    request = {
        'type': 'anime movie',
        'size': 1000,
        'country': 'Japan',
        'genres': 'animation'
    }
    try:
        await ctx.send(user_request_response(ctx.author, request, args))
        res = requests.get(url=URL, params=build_params(args))
        data = res.json()
        await ctx.send(embed=motion_picture_embed(ctx.author, data))
    except requests.exceptions.RequestException as e:
        await ctx.send("No animes found with those criteria")

def motion_picture_embed(author, data):
    embed = discord.Embed(title=f"🍿 **{data['title']}** 🎬", description="", color=0x00ff00)
    embed.set_author(name=f"{get_name(author)}", url="", icon_url=author.avatar_url)
    embed.add_field(name="\u200b", value=f"{data['plot']}", inline=False)
    embed.add_field(name="Release Date 🗓 ", value=f"{data['year']}", inline=True)
    embed.add_field(name="Rating ⭐️", value=f"{data['rating']}⭐️ from {data['votes']} users 🕺", inline=False)
    country = pycountry.countries.search_fuzzy(data['country'])[0]
    name, emoji = get_country_info(country.alpha_2)
    embed.add_field(name="Runtime ⏱", value=f"{get_common_time(data['runtime'])}", inline=False)
    embed.add_field(name="Country", value=f"{name} {emoji}", inline=False)
    embed.add_field(name="Genres", value=f"{data['genres']}", inline=False)
    embed.add_field(name="Awards 🏆", value=f"{data['awards']}", inline=False)
    embed.set_image(url=data['poster'])
    embed.add_field(name="\u200b", value="Contribute to this bot [here](https://github.com/JustinLiAtSBU/magic-eight-ball-bot)")
    return embed

def user_request_response(author, request, args):
    response = f"✨ Your request is in {get_name(author)} ✨ \n\n"
    response += f"You want to watch a random {request['type']} out of the top {request['size']} movies on **IMDB**...\n"
    for arg in args:
        key = arg.split('=')[0]
        value = arg.split('=')[1]
        if arg == args[-1]:
            response += 'and '
        if key == 'year':
            response += f'made after {value} 🗓 ...\n'
        elif key == 'runtime':
            response += f'with a minimum {key} of {value} ⏱ minutes...\n'
        elif key == 'country':
            name, emoji = get_country_info(value)
            response += f'from {name} {emoji}\n'
        elif key == 'genres':
            genres = genre_match(value.split(','))
            response += f"with the genre {', '.join(genres)}" if len(genres) == 1 else f"with the genres {', '.join(genres)}"
        else:
            response += f'a minimum {key} of {value}\n'
    response += f'\n\n🥁 **Your random {request["type"]} is... **🥁\n\n'
    return response

def get_country_info(country_code):
    country = pycountry.countries.get(alpha_2=country_code)
    name = country.name
    if hasattr(country, 'common_name'):
        name = country.common_name
    emoji = flag.flag(country_code)
    return name, emoji

def get_common_time(time):
    common_time = f""
    hours = time // 60
    minutes = time % 60
    if hours:
        common_time += f"{hours} hours "
    if minutes:
        common_time += f"and {minutes} minutes"
    return common_time

def build_params(args):
    PARAMS = { 'size': 100 }
    for arg in args:
        key, value = arg.split('=')
        if key not in NON_MIN_QUERY_PARAMS:
            PARAMS[f'min{key.capitalize()}'] = value
        else:
            PARAMS[key] = value
    return PARAMS


bot.run(TOKEN)