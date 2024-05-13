import re
import os
from sys import argv
from configparser import ConfigParser

from pytube import YouTube
from yt_dlp import YoutubeDL

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')

OUT_PATH = config['PATHS']['OUT_PATH']
FFMPEG_PATH = config['PATHS']['FFMPEG_PATH']

class Single():
    @staticmethod
    def set_out_path(path: str):
        global OUT_PATH
        OUT_PATH = path
    
    @staticmethod
    def download(url: str, audio_only: bool = False):
        if(not os.path.isdir(OUT_PATH)):
            raise SystemExit(f'Out path does not exist {OUT_PATH}')
        url = url.split('&')[0]
        try:
            with YoutubeDL() as ytdl:
                title = ytdl.extract_info(url, download = False).get('title', None)
            ## y = YouTube(url = url)
        except Exception as e:
            print(f'Exception: {e}')
            exit(1)
            
        print(f'Title: {title}')
        ## print('Available versions:')

        ## GET ALL VIDEOS AND SORT BY RESOLUTION
        ## video_list = list(y.streams.filter(type = 'video').order_by('resolution'))
        ## print(*y.streams, sep = '\n')
        ## highest_res = video_list[-1]
        ## the command below does not have the desired behaviour
        ## highest_res = y.streams.filter(file_extension = 'mp4').get_highest_resolution()
        ## https://pytube.io/en/latest/user/streams.html?highlight=progressive#dash-vs-progressive-streams
        ## see the documentation in the webpage linked above for explanation
        ## generally the documentation is adequate - sufficiently succinct
        ## though it does include some ambiguities, for example it claims that
        ## 'resolution' is used as an alias of 'res', even though for ordering
        ## streams the correct name is the first, as seen by looking at the object's __dict__
        ## print(f'The version with the highest resolution: {highest_res}')

        ## GET SANITIZED TITLE FOR FILENAMES AND FILE EXTENSION
        title = re.sub(r'[^\u0370-\u03ff\u1f00-\u1fffa-zA-Z0-9 ]', '', title)
        ## the regular expression above matches all greek and latin characters, the digits and the space
        title = ' '.join(title.split())
        ## extension = highest_res.default_filename.split('.')[1]
        ## video_filename = f'{title}.{extension}'
        video_filename = f'{title}_video.mp4'

        ## DOWNLOAD HIGHEST RESOLUTION
        if(not audio_only):
            ## highest_res.download(output_path = OUT_PATH, filename = video_filename)
            print('Downloading highest resolution video')
            try:
                os.system(f'yt-dlp -f bestvideo[ext=mp4] -o "{OUT_PATH}\\{video_filename}" {url}')
            except Exception as e:
                print(f'Exception: {e}')
                exit(1)

        ## EXAMINE IF THE HIGHEST RESOLUTION VIDEO IS "PROGRESSIVE", THAT
        ## IS, IF IT CONTAINS SOUND
        '''
        if(highest_res.is_progressive == True):
            print('Highest resolution video file contains audio.')
        '''

        ## IF NOT, DOWNLOAD AUDIO FILE SEPARATELY AND MERGE THE TWO WITH FFMPEG
        ## else:
        ## print('Highest resolution video file does not contain sound. Available audio files:')
        ## TODO: prioritize mp4 audio over webm
        ## audio_list = list(y.streams.filter(type = 'audio', subtype = 'mp4').order_by('abr'))
        '''
        if(not audio_list):
            audio_list = list(y.streams.filter(type = 'audio').order_by('abr'))
        ## print(*audio_list, sep = '\n')
        highest_br = audio_list[-1]
        print(f'The version with the highest bit rate: {highest_br}')
        
        extension = highest_br.default_filename.split('.')[1]
        '''
        print('Downloading audio')
        audio_filename = f'{title}_audio.mp4'
        try:
            ## highest_br.download(output_path = OUT_PATH, filename = audio_filename)
            os.system(f'yt-dlp -f bestaudio[ext=mp4] -o "{OUT_PATH}\\{audio_filename}" {url}')
        except Exception as e:
            print(f'Exception: {e}')
            exit(1)
        if(not audio_only):
            print('Merging files with ffmpeg')
            if(os.path.isfile(f'{OUT_PATH}\\{audio_filename}') and os.path.isfile(f'{OUT_PATH}\\{video_filename}')):
                try:
                    os.system(f'{FFMPEG_PATH}\\ffmpeg -i "{OUT_PATH}\\{video_filename}" -i "{OUT_PATH}\\{audio_filename}" -c copy "{OUT_PATH}\\{title}.mp4"')
                    os.remove(f'{OUT_PATH}\\{video_filename}')
                    os.remove(f'{OUT_PATH}\\{audio_filename}')
                except Exception as e:
                    print(f'Exception: {e}')
                    exit(1)
        
if(__name__ == '__main__'):
    if(len(argv) != 2 and len(argv) != 3):
        print('Invalid arguments')
        exit(1)
    if(len(argv) == 3 and argv[2] != '/a'):
        print('Invalid third argument')
        exit(1)
    Single.download(argv[1], len(argv) == 3)
