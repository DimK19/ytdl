import sys
from time import sleep
from configparser import ConfigParser
import os
import re
from pathlib import Path

from single import Single, SingleException

from pytube import Playlist

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')
OUT_PATH = Path(config['PATHS']['OUT_PATH'])

def main():
    p = Playlist(sys.argv[1])
    directory = Path.joinpath(OUT_PATH, re.sub(r'[^\u0370-\u03ff\u1f00-\u1fffa-zA-Z0-9 ]', '', p.title))
    if(not os.path.isdir(directory)):
        os.mkdir(str(directory))
    Single.set_out_path(directory)
    ## i = 0
    ## skip = 0
    for v in p.url_generator():
        ## skip += 1
        ## Μπαμπινιώτης:
        ## https://www.youtube.com/playlist?list=PL9wtvO3_pCB1BRuwbwI8-u3i3-CW3YX-y
        ## Κούτυλας:
        ## https://www.youtube.com/playlist?list=PLi1hj7aavfxy7k6SOaNcM6OneaUFmhwUD
        ## if(skip < 97):
            ## continue
        try:
            Single.download(v, len(sys.argv) == 3)
        except SingleException as e:
            print(f'Exception: {e}')
            continue
        ## i += 1
        ## if(i == 10):
        ##    break
        sleep(30)

if(__name__ == '__main__'):
    if(len(sys.argv) != 2 and len(sys.argv) != 3):
        print('Invalid arguments')
        sys.exit(1)
    if(len(sys.argv) == 3 and sys.argv[2] != '/a'):
        print('Invalid third argument')
        sys.exit(1)
    main()
