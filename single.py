import re
import os
import sys
from configparser import ConfigParser
import pickle
from pathlib import Path
import argparse

from yt_dlp import YoutubeDL

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')

OUT_PATH = Path(config['PATHS']['OUT_PATH'])
FFMPEG_PATH = Path(config['PATHS']['FFMPEG_PATH'])
PKLP = Path.joinpath(OUT_PATH, 'preexisting.pkl')

PREEXISTING = []

def sanitize(s: str):
    res = re.sub(r'[^\u0370-\u03ff\u1f00-\u1fffa-zA-Z0-9 ]', '', s.strip())
    ## the regular expression above matches all greek and latin characters, the digits and the space
    return ' '.join(res.split())

class SingleException(Exception):
    _message = 'Exception from Single'

    def __init__(self, m: str = _message):
        self._message = m

    def __str__(self):
        return self._message

class Single():
    @staticmethod
    def set_out_path(p: str):
        global OUT_PATH, PREEXISTING, PKLP
        OUT_PATH = Path(p)
        if(not os.path.isdir(OUT_PATH)):
            raise Systemsys.exit(f'Out path does not exist {str(OUT_PATH)}')

        PKLP = Path.joinpath(OUT_PATH, 'preexisting.pkl')
        if(os.path.isfile(PKLP)):
            with open(str(PKLP), 'rb') as f:
                PREEXISTING = pickle.load(f)
        else:
            PREEXISTING = list(map(lambda x: x.split('.')[0], os.listdir(OUT_PATH)))

    @staticmethod
    def download(url: str, t: str = None, audio_only: bool = False):
        url = url.split('&')[0]

        if(t is None)
            try:
                with YoutubeDL() as ytdl:
                    original_title = ytdl.extract_info(url, download = False).get('title', None)
            except Exception as e:
                if(__name__ == '__main__'):
                    print(f'Exception: {e}')
                    sys.exit(1)
                else:
                    raise SingleException(f'{e}')
        else:
            original_title = t
        print(f'Title: {original_title}')

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
        title = sanitize(original_title)
        '''
        if(title in PREEXISTING):
            if(__name__ == '__main__'):
                print('Video already downloaded.')
                sys.exit(0)
            else:
                raise SingleException('Video already downloaded.')
        '''
        ## extension = highest_res.default_filename.split('.')[1]

        ytdl_title = f"{original_title} [{url.split('/')[-1].split('&')[0][8:]}]"
        ## DOWNLOAD HIGHEST RESOLUTION
        if(not audio_only):
            ## highest_res.download(output_path = OUT_PATH, filename = video_filename)
            print('Downloading highest resolution video')
            try:
                cmd = os.system(f'yt-dlp -f bestvideo -P "{str(OUT_PATH)}" {url}')
                ## cmd = os.system(f'yt-dlp -f bestvideo --cookies-from-browser firefox -P "{str(OUT_PATH)}" {url}')
                '''
                WARNING: "-f best" selects the best pre-merged format which is often not the best option.
                To let yt-dlp download and merge the best available formats, simply do not pass any format selection.
                If you know what you are doing and want only the best pre-merged format, use "-f b" instead to suppress this warning
                '''
                if(cmd != 0):
                    raise SingleException('YTDLP Error')
            except Exception as e:
                if(__name__ == '__main__'):
                    print(f'Exception: {e}')
                    sys.exit(1)
                else:
                    raise SingleException(f'{e}')

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

            ## GET NAME OF DOWNLOADED VIDEO
            new_file = None
            new_ext = None
            for i in os.listdir(OUT_PATH):
                ## YT video title may contain '.'
                if(sanitize('.'.join(i.split('.')[:-1])) == sanitize(ytdl_title)):
                    new_file = i
                    new_ext = i.split('.')[-1]
                    break

            if(not(new_file is None)):
                video_filename = Path.joinpath(OUT_PATH, f'{title}_video.{new_ext}')
                os.rename(str(Path.joinpath(OUT_PATH, new_file)), str(video_filename))
            else:
                raise SingleException()
                exit(1)

        print('Downloading audio')
        try:
            ## highest_br.download(output_path = OUT_PATH, filename = audio_filename)
            ## os.system(f'yt-dlp -f bestaudio[ext=mp4] -o "{OUT_PATH}\\{audio_filename}" {url}')
            ## os.system(f'yt-dlp -f bestaudio --cookies-from-browser firefox -P "{str(OUT_PATH)}" {url}')
            os.system(f'yt-dlp -f bestaudio -P "{str(OUT_PATH)}" {url}')
        except Exception as e:
            if(__name__ == '__main__'):
                print(f'Exception: {e}')
                sys.exit(1)
            else:
                raise SingleException(f'{e}')

        ## GET NAME OF DOWNLOADED AUDIO
        new_file_audio = None
        new_ext_audio = None
        for i in os.listdir(OUT_PATH):
            if(sanitize('.'.join(i.split('.')[:-1])) == sanitize(ytdl_title)):
                new_file_audio = i
                new_ext_audio = i.split('.')[-1]
                break

        if(not audio_only):
            print('Merging files with ffmpeg')

            audio_filename = Path.joinpath(OUT_PATH, f'{title}_audio.{new_ext_audio}')
            os.rename(str(Path.joinpath(OUT_PATH, new_file_audio)), str(audio_filename))

            if(os.path.isfile(audio_filename) and os.path.isfile(video_filename)):
                try:
                    merged_filename = Path.joinpath(OUT_PATH, f'{title}.{new_ext}')
                    cmd = os.system(f'{str(Path.joinpath(FFMPEG_PATH, "ffmpeg"))} -i "{str(video_filename)}" -i "{str(audio_filename)}" -c copy "{str(merged_filename)}"')
                    if(cmd == 0):
                        os.remove(str(video_filename))
                        os.remove(str(audio_filename))
                    else:
                        raise SingleException('FFMPEG Error')
                except Exception as e:
                    if(__name__ == '__main__'):
                        print(f'Exception: {e}')
                        sys.exit(1)
                    else:
                        raise SingleException(f'{e}')
        else:
            audio_filename = Path.joinpath(OUT_PATH, f'{title}.{new_ext_audio}')
            os.rename(str(Path.joinpath(OUT_PATH, new_file_audio)), str(audio_filename))

        ## Finally append new file name to pickle
        PREEXISTING.append(title)
        with open(PKLP, 'wb') as f:
            pickle.dump(PREEXISTING, f)

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
    args = parser.parse_args()

    Single.set_out_path(OUT_PATH)
    Single.download(url = args.url, audio_only = args.audio_only)
