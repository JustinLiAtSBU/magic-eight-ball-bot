import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
FRIENDS_CSV = os.getenv('FRIENDS')
friends = {}
if FRIENDS_CSV is not None:
    friends_array = FRIENDS_CSV.split(',')
    for mapping in friends_array:
        username = mapping.split(':')[0]
        real_name = mapping.split(':')[1]
        friends[username] = real_name

def get_friends():
    return friends

def get_name(author: discord.Member):
    full_username = f'{author.name}#{author.discriminator}'
    return friends[full_username] if full_username in friends else full_username
