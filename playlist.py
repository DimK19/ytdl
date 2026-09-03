import argparse
from time import sleep
from configparser import ConfigParser
import os
import sys
from pathlib import Path
from itertools import islice

from single import Single, SingleException
from string_utils import sanitize

from yt_dlp import YoutubeDL

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')
OUT_PATH = Path(config['PATHS']['OUT_PATH'])

try:
    with open('premiumTitles.txt', 'r', encoding = 'utf-8') as f:
        premium_names = list(map(lambda x: x.rstrip('\n'), f.readlines()))
except:
    premium_names = []
    
premium = False
audio_only = False
skip = 0
stop = None
url = ''
cn = ''

def get_playlist_title(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download = False)
            return info.get('title')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

def url_generator(u):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  ## Don't download metadata for each video
        'force_generic_extractor': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(url, download = False)

        if('entries' not in playlist_dict):
            raise ValueError('Invalid playlist URL or no entries found.')

        for entry in playlist_dict['entries']:
            ## Each entry is a dict with 'url' and optionally 'title' etc.
            yield f"https://www.youtube.com/watch?v={entry['id']}"

def main():
    directory = Path.joinpath(OUT_PATH, sanitize(get_playlist_title(url)))
    if(not os.path.isdir(directory)):
        os.mkdir(str(directory))
    Single.set_out_path(directory)

    generator = islice(url_generator(url), skip, (None if stop is None else stop + skip))
    if(not premium):
        for u in generator:
            try:
                Single.download(url = u, audio_only = audio_only)
            except SingleException as e:
                print(f'Exception: {e}')
                continue
            sleep(20)
    else:
        for t, u in zip(premium_names, generator):
            try:
                Single.download(
                    url = u,
                    t = t,
                    cn = cn,
                    audio_only = audio_only,
                    premium = premium,
                    resolution = res
                )
            except SingleException as e:
                print(f'Exception: {e}')
                continue
            sleep(20)

if(__name__ == '__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u',
        '--url',
        dest = 'url',
        type = str,
        required = True,
        help = 'The URL of the video to be downloaded'
    )

    ## Boolean flags
    parser.add_argument(
        '--premium',
        dest = 'premium',
        action = 'store_true',
        help = 'Use cookies from firefox to download premium video'
    )
    parser.add_argument(
        '--audio-only',
        dest = 'audio_only',
        action = 'store_true',
        help = 'Download audio only'
    )

    ## Integer arguments
    parser.add_argument(
        '--skip',
        dest = 'pl_skip',
        type = int,
        default = 0,
        help = 'Number of items to skip in the playlist before starting downloading'
    )
    parser.add_argument(
        '--stop',
        dest = 'pl_stop',
        type = int,
        default = None,
        help = 'Stop downloading after this many playlist items'
    )

    ## Additional options
    parser.add_argument(
        '--cn',
        dest = 'channel_name',
        type = str,
        default = None,
        help = 'The name of the channel publishing the video'
    )
    
    parser.add_argument(
        '--res',
        dest = 'resolution',
        type = int,
        default = None,
        help = 'The video resolution height in pixels'
    )

    args = parser.parse_args()
    
    if(args.premium and (args.channel_name is None)):
        parser.error('--premium requires the specification of a channel name with --cn, because it can not be extracted automatically.')

    url = args.url
    audio_only = args.audio_only
    premium = args.premium
    cn = args.channel_name
    skip = args.pl_skip
    stop = args.pl_stop
    res = args.resolution

    main()
