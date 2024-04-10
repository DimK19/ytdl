from sys import argv
from time import sleep
from configparser import ConfigParser
import os

from pytube import Playlist

from single import Single

config = ConfigParser()
config.read('config.ini')
OUT_PATH = config['PATHS']['OUT_PATH']

def main():
    p = Playlist(argv[1])
    directory = OUT_PATH + '\\' + p.title
    if(not os.path.isdir(directory)):
        os.system(f'mkdir "{directory}"')
    Single.set_out_path(directory)
    for v in p.url_generator():
        Single.download(v, len(argv) == 3)
        sleep(3)

if(__name__ == '__main__'):
    if(len(argv) != 2 and len(argv) != 3):
        print('Invalid arguments')
        exit(1)
    if(len(argv) == 3 and argv[2] != '/a'):
        print('Invalid third argument')
        exit(1)
    main()
