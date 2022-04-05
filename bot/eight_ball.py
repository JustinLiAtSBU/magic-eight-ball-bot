import os
import discord
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
    URL = f'{API}/api/movies/random'
    PARAMS = {
        'size': top
    }

    response = f'✨ Your request is in {get_name(ctx.author)} ✨ \n\n'
    response += f'You want to watch a random movie out of the top {top} movies on **IMDB**...\n'
    for arg in args:
        key = arg.split('=')[0]
        value = arg.split('=')[1]
        PARAMS[f'min{key.capitalize()}'] = value
        if arg == args[-1]:
            response += 'and '
        if key == 'year':
            response += f'made after {value} 🗓 ...\n'
        elif key == 'runtime':
            response += f'with a minimum {key} of {value} ⏱ minutes...\n'
        else:
            response += f'a minimum {key} of {value}\n'

    res = requests.get(url = URL, params = PARAMS)
    data = res.json()

    response += f'\n🥁 **Your random movie is... **🥁\n\n'
    response += "> {}".format(f"🍿 **{data['title']} ** 🎬 \n")
    response += "> {}".format("\n")
    response += "> {}".format(f"Released in **{data['year']}** 🗓 \n")
    response += "> {}".format(f"With a rating of **{data['rating']}**⭐️ from **{data['votes']}** users 🕺 \n")
    response += "> {}".format(f"Length: **{data['runtime']} minutes** ⏱ \n")
    response += "> {}".format(f"Genres: *{data['genres']}*")

    await ctx.send(response) 


bot.run(TOKEN)
