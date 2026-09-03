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

PREEXISTING = dict()

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

    @staticmethod
    def download(
        url: str,
        t: str = None,
        cn: str = None,
        audio_only: bool = False,
        premium: bool = False,
        resolution: int = None
    ):
        url = url.split('&')[0]

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            with YoutubeDL(ydl_opts) as ytdl:
                info = ytdl.extract_info(url, download = False)
                original_title = t if t else info.get('title', 'NO TITLE')
                channel_name = cn if cn else info.get('channel', '')
        except Exception as e:
            if(__name__ == '__main__'):
                print(f'Exception: {e}')
                sys.exit(1)
            else:
                raise SingleException(f'{e}')

        print(f'Title: {original_title}')
        
        ## Grab the video ID from the metadata dictionary if not manually passed, 
        ## but since yt-dlp extracted it, it's safer. Fallback just in case.
        video_id = info.get('id') if 'info' in locals() else url.split('v=')[-1][:11]

        ## GET SANITIZED TITLE FOR FILENAMES AND FILE EXTENSION
        title = f'{sanitize(original_title)} - {sanitize(channel_name)} [{video_id}]'
        video_template = Path.joinpath(OUT_PATH, f'{title}_video.%(ext)s')
        audio_template = Path.joinpath(OUT_PATH, f'{title}_audio.%(ext)s')

        if(video_id in PREEXISTING):
            if(__name__ == '__main__'):
                print('Video already downloaded.')
                sys.exit(0)
            else:
                raise SingleException('Video already downloaded.')

        ## DOWNLOAD HIGHEST RESOLUTION
        if(not audio_only):
            print('Downloading highest resolution video')
            try:
                command = 'yt-dlp --js-runtimes node'
                if(resolution is not None):
                    command += f' -S "+height:{resolution}"'
                command += ' -f bestvideo'
                command += " --cookies-from-browser firefox"
                command += f' -o "{str(video_template)}" {url}'
                
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
            '''
            for i in os.listdir(OUT_PATH):
                if i.startswith(f'{title}_video.'):
                    video_filename = Path.joinpath(OUT_PATH, i)
                    new_ext = video_filename.suffix[1:]
                    break
            '''
            try:
                # glob returns a generator, list()[0] gets the actual Path object
                video_filename = list(OUT_PATH.glob(f'*{video_id}*_video.*'))[0]
                new_ext = video_filename.suffix[1:]
            except IndexError:
                raise SingleException('Downloaded video file could not be found.')

        print('Downloading audio')
        try:
            command = 'yt-dlp --remote-components ejs:github --js-runtimes node -f bestaudio'
            command += ' --cookies-from-browser firefox'
            command += f' -o "{str(audio_template)}" {url}'
            
            os.system(command)
        except Exception as e:
            if(__name__ == '__main__'):
                print(f'Exception: {e}')
                sys.exit(1)
            else:
                raise SingleException(f'{e}')

        ## GET NAME OF DOWNLOADED AUDIO
        '''
        for i in os.listdir(OUT_PATH):
            if i.startswith(f'{title}_audio.'):
                audio_filename = Path.joinpath(OUT_PATH, i)
                new_ext_audio = audio_filename.suffix[1:]
                break
        '''
        try:
            audio_filename = list(OUT_PATH.glob(f'*{video_id}*_audio.*'))[0]
            new_ext_audio = audio_filename.suffix[1:]
        except IndexError:
            raise SingleException('Downloaded audio file could not be found.')
        
        if(not audio_only):
            print('Merging files with ffmpeg')

            if(os.path.isfile(audio_filename) and os.path.isfile(video_filename)):
                try:
                    merged_filename = Path.joinpath(OUT_PATH, f'{title}.{new_ext}')
                    cmd = os.system(f'{str(Path.joinpath(FFMPEG_PATH, "ffmpeg"))} -i "{str(video_filename)}" -i "{str(audio_filename)}" -c copy "{str(merged_filename)}"')
                    if(cmd == 0):
                        pass
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
            final_audio_filename = Path.joinpath(OUT_PATH, f'{title}.{new_ext_audio}')
            os.rename(str(audio_filename), str(final_audio_filename))

        ## Finally append new file name to pickle
        PREEXISTING[video_id] = original_title
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

    Single.set_out_path(OUT_PATH)
    Single.download(
        url = args.url,
        cn = args.channel_name,
        audio_only = args.audio_only,
        premium = args.premium,
        resolution = args.resolution
    )
