import os
import discord
import flag
import pycountry
import random
import requests
from dotenv import load_dotenv
from discord.ext import commands
from personalize import get_name, get_friends


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API = os.getenv('MAGIC_EIGHT_BALL_API')
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')

@bot.command(name='test', help='Tests whether the bot is running')
async def test(ctx):
    await ctx.send('OK')

@bot.command(name='hello', help='Sends a little hello')
async def hello(ctx):
    await ctx.send(f'Hello {get_name(ctx.author)}')

@bot.command(name='whoisstreaming', help='Tells you who is going to stream')
async def who_streaming(ctx):
    members = [i for i in ctx.channel.members if i.bot is not True]
    streamer = random.choice(members)
    await ctx.send(f"You're streaming {get_name(streamer)}")

@bot.command(name='randommovie', help='Gives you a random movie to watch. If no arguments are passed, we pick a random movie made after 1990 with a rating of 7+')
async def random_movie(ctx, top, *args):
    request = {
        'type': 'movie',
        'top': top
    }
    URL = f'{API}/api/movies/random'
    PARAMS = { 'size': top }

    for arg in args:
        key = arg.split('=')[0]
        value = arg.split('=')[1]
        if key != 'country':
            PARAMS[f'min{key.capitalize()}'] = value
        else:
            PARAMS[key] = value
    print(PARAMS)
    try:
        res = requests.get(url = URL, params = PARAMS)
        data = res.json()
        response, embed = response_builder(ctx.author, request, args, data)
        await ctx.send(response)
        await ctx.send(embed=embed)
    except requests.exceptions.RequestException as e:
        await ctx.send("No movies found with those criteria")


@bot.command(name='randomtvshow', help='Gives you a random TV show to watch. If no arguments are passed, we pick a random TV show made after 1990 with a rating of 7+')
async def random_tv_show(ctx, top, *args):
    request = {
        'type': 'tvSeries',
        'top': top
    }
    URL = f'{API}/api/tvshows/random'
    PARAMS = { 'size': top }

    for arg in args:
        key = arg.split('=')[0]
        value = arg.split('=')[1]
        if key != 'country':
            PARAMS[f'min{key.capitalize()}'] = value
        else:
            PARAMS[key] = value
    print(PARAMS)
    try:
        res = requests.get(url = URL, params = PARAMS)
        data = res.json()
        response, embed = response_builder(ctx.author, request, args, data)
        await ctx.send(response)
        await ctx.send(embed=embed)
    except requests.exceptions.RequestException as e:
        await ctx.send("No TV shows found with those criteria")
    

def response_builder(author, request, args, data):
    response = f"✨ Your request is in {get_name(author)} ✨ \n\n"
    response += f"You want to watch a random {request['type']} out of the top {request['top']} movies on **IMDB**...\n"
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
            response += f'from {name} {emoji}'
        else:
            response += f'a minimum {key} of {value}\n'
    response += f'\n\n🥁 **Your random {request["type"]} is... **🥁\n\n'

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

    return response, embed


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


bot.run(TOKEN)