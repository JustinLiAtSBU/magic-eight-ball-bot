import os
import requests
from typing import Final


API = os.getenv('MAGIC_EIGHT_BALL_API')
PATH_MAP: Final = {
    'movie': 'api/movies/random',
    'TV show': 'api/tvshows/random',
    'anime': 'api/tvshows/random',
    'anime movie': 'api/movies/random',
}
NON_MIN_QUERY_PARAMS: Final = ['country', 'size', 'genres']


def build_and_send_request(request, args):
    url = f"{API}/{PATH_MAP[request['type']]}"
    print(url)
    res = requests.get(url=url, params=build_params(args))
    return res.json()

def build_params(args):
    PARAMS = { 'size': 100 }
    for arg in args:
        key, value = arg.split('=')
        if key not in NON_MIN_QUERY_PARAMS:
            PARAMS[f'min{key.capitalize()}'] = value
        else:
            PARAMS[key] = value
    return PARAMS
