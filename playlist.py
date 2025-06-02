## https://superuser.com/questions/1804415/how-to-get-playlist-title-with-yt-dlp
## https://github.com/yt-dlp/yt-dlp/issues/2117
import argparse
from time import sleep
from configparser import ConfigParser
import os
import re
from pathlib import Path
from itertools import islice

from single import Single, SingleException

from pytube import Playlist

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')
OUT_PATH = Path(config['PATHS']['OUT_PATH'])

premium_names = []
premium = False
audio_only = False
skip = 0
stop = None
url = ''

def main():
    p = Playlist(url)
    directory = Path.joinpath(OUT_PATH, re.sub(r'[^\u0370-\u03ff\u1f00-\u1fffa-zA-Z0-9 ]', '', p.title))
    if(not os.path.isdir(directory)):
        os.mkdir(str(directory))
    Single.set_out_path(directory)
    i = 0
    generator = itertools.islice(p.url_generator, skip, stop - skip)
    ##for t, u in zip(premium, p.url_generator()):
    for u in generator:
        ## Μπαμπινιώτης:
        ## https://www.youtube.com/playlist?list=PL9wtvO3_pCB1BRuwbwI8-u3i3-CW3YX-y
        ## Κούτυλας premium:
        ## https://www.youtube.com/playlist?list=PLi1hj7aavfxy7k6SOaNcM6OneaUFmhwUD
        ## Κούτυλας:
        ## https://www.youtube.com/playlist?list=PLi1hj7aavfxwqSLv1rkzuHn3_D4TR2dvo
        try:
            Single.download(url = u, audio_only = audio_only, premium = premium)
            ## os.system(f'yt-dlp --cookies-from-browser firefox -P "{str(OUT_PATH)}" {v}')
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
        '--playlist-skip',
        dest = 'pl_skip',
        type = int,
        default = 0,
        help = 'Number of items to skip in the playlist before starting downloading'
    )
    parser.add_argument(
        '--playlist-stop',
        dest = 'pl_stop',
        type = int,
        default = None,
        help = 'Stop downloading after this many playlist items'
    )
    args = parser.parse_args()
    audio_only = args.audio_only
    premium = args.premium
    skip = args.pl_skip
    stop = args.pl_stop
    main()
