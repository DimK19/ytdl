import os
import sys
from configparser import ConfigParser
import pickle
from pathlib import Path
import argparse

from string_utils import sanitize

from yt_dlp import YoutubeDL

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')

OUT_PATH = Path(config['PATHS']['OUT_PATH'])
FFMPEG_PATH = Path(config['PATHS']['FFMPEG_PATH'])
PKLP = Path.joinpath(OUT_PATH, 'preexisting.pkl')

PREEXISTING = set()

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
            PREEXISTING = set(map(lambda x: x.split('.')[0], os.listdir(OUT_PATH)))

    @staticmethod
    def download(url: str, t: str = None, audio_only: bool = False, premium: bool = False):
        url = url.split('&')[0]

        if(t is None):
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }
                with YoutubeDL(ydl_opts) as ytdl:
                    info = ytdl.extract_info(url, download = False)
                    original_title = info.get('title', 'NO TITLE')
                    channel_name = info.get('channel', '')
            except Exception as e:
                if(__name__ == '__main__'):
                    print(f'Exception: {e}')
                    sys.exit(1)
                else:
                    raise SingleException(f'{e}')
        else:
            original_title = t
            channel_name = ''
        print(f'Title: {original_title}')

        ## GET SANITIZED TITLE FOR FILENAMES AND FILE EXTENSION
        title = f'{sanitize(original_title)} [{sanitize(channel_name)}]'
        
        if(title in PREEXISTING):
            if(__name__ == '__main__'):
                print('Video already downloaded.')
                sys.exit(0)
            else:
                raise SingleException('Video already downloaded.')

        ytdl_title = f"{original_title} [{url.split('/')[-1].split('&')[0][8:]}]"
        ## DOWNLOAD HIGHEST RESOLUTION
        if(not audio_only):
            print('Downloading highest resolution video')
            try:
                command = f'yt-dlp -f bestvideo{" --cookies-from-browser firefox" if premium else ""} -P "{str(OUT_PATH)}" {url}'
                cmd = os.system(command)
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
            command = f'yt-dlp -f bestaudio{" --cookies-from-browser firefox" if premium else ""} -P "{str(OUT_PATH)}" {url}'
            os.system(command)
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
        PREEXISTING.add(title)
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
