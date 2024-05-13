from sys import argv
from time import sleep
from configparser import ConfigParser
import os
import re

from pytube import Playlist

from single import Single

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')
OUT_PATH = config['PATHS']['OUT_PATH']

def main():
    p = Playlist(argv[1])
    directory = OUT_PATH + '\\' + re.sub(r'[^\u0370-\u03ff\u1f00-\u1fffa-zA-Z0-9 ]', '', p.title)
    if(not os.path.isdir(directory)):
        os.system(f'mkdir "{directory}"')
    Single.set_out_path(directory)
    ## i = 0
    ## counter = 0
    for v in p.url_generator():
        ## counter += 1
        ## https://www.youtube.com/playlist?list=PL9wtvO3_pCB1BRuwbwI8-u3i3-CW3YX-y
        ## if(counter < 97):
            ## continue
        Single.download(v, len(argv) == 3)
        ## i += 1
        sleep(30)

if(__name__ == '__main__'):
    if(len(argv) != 2 and len(argv) != 3):
        print('Invalid arguments')
        exit(1)
    if(len(argv) == 3 and argv[2] != '/a'):
        print('Invalid third argument')
        exit(1)
    main()
