import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
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
    await ctx.send(f'Hello {ctx.author}')

@bot.command(name='whostreaming', help='Tells you who is going to stream')
async def who_streaming(ctx):
    members = [i for i in ctx.channel.members if i.bot is not True]
    streamer = random.choice(members)
    await ctx.send(f"You're streaming {streamer}")

bot.run(TOKEN)
