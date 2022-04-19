import os
import discord
import flag
import pycountry
from dotenv import load_dotenv
from fuzzy_match import genre_match


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

def get_name(author):
    if type(author) is discord.Member:
        full_username = f'{author.name}#{author.discriminator}'
        return friends[full_username] if full_username in friends else full_username
    else:
        return friends[author] if author in friends else author

def motion_picture_embed(author, data):
    embed = discord.Embed(title=f"🍿 **{data['title']}** 🎬", description="", color=0x00ff00)
    embed.set_author(name=f"{get_name(author)}", url="", icon_url=author.avatar.url)
    embed.add_field(name="\u200b", value=f"{data['plot']}", inline=False)
    embed.add_field(name="Release Date 🗓 ", value=f"{data['year']}", inline=True)
    embed.add_field(name="Rating ⭐️", value=f"{data['rating']}⭐️ from {data['votes']} users 🕺", inline=False)
    country = pycountry.countries.search_fuzzy(data['country'])[0]
    name, emoji = get_country_info(country.alpha_2)
    embed.add_field(name="Runtime ⏱", value=f"{get_common_time(data['runtime'])}", inline=False)
    embed.add_field(name="Country", value=f"{name} {emoji}", inline=False)
    embed.add_field(name="Genres", value=f"{', '.join(data['genres'])}", inline=False)
    embed.add_field(name="Awards 🏆", value=f"{data['awards']}", inline=False)
    embed.set_image(url=data['poster'])
    embed.add_field(name="\u200b", value="Contribute to this bot [here](https://github.com/JustinLiAtSBU/magic-eight-ball-bot)")
    return embed

def user_request_response(author, request, args):
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
            response += f'from {name} {emoji}\n'
        elif key == 'genres':
            genres = genre_match(value.split(','))
            response += f"with the genre {', '.join(genres)}" if len(genres) == 1 else f"with the genres {', '.join(genres)}"
        elif key != 'top':
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

def progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = round(length * iteration // total)
    bar = fill * filled_length + '─' * (length - filled_length)
    return f"\r{prefix} |{bar}| {percent}% {suffix}"
