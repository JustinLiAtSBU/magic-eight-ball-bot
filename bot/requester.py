import os
import requests
from typing import Final


API = os.getenv('MAGIC_EIGHT_BALL_API')
PATH_MAP: Final = {
    'movie': 'movies/random',
    'TV show': 'tvshows/random',
    'anime': 'tvshows/random',
    'anime movie': 'movies/random',
    'create/update channel': 'channels/create',
    'update_channels_watched_movies': 'channels/updatewatchedmovies',
    'update_channels_watched_tv_shows': 'channels/updatewatchedtvshows',
}
NON_MIN_QUERY_PARAMS: Final = ['country', 'top', 'genres']


async def random_motion_picture_request(request, args):
    url = f"{API}/{PATH_MAP[request['type']]}"
    res = requests.get(url=url, params=build_params(args))
    return res.json()

async def create_channel_request(params, body):
    url = f"{API}/{PATH_MAP['create/update channel']}"
    res = requests.post(url=url, params=params, json=body)
    return res

async def update_channels_watched_movies(channel_id, body):
    url = f"{API}/{PATH_MAP['update_channels_watched_movies']}/{channel_id}"
    res = requests.put(url, json=body)
    return res

async def update_channels_watched_tv_shows(channel_id, body):
    url = f"{API}/{PATH_MAP['update_channels_watched_tv_shows']}/{channel_id}"
    res = requests.put(url, json=body)
    return res

def build_params(args):
    PARAMS = {}
    for arg in args:
        key, value = arg.split('=')
        if key not in NON_MIN_QUERY_PARAMS:
            PARAMS[f'min{key.capitalize()}'] = value
        else:
            PARAMS[key] = value
    return PARAMS
