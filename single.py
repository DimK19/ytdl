import re
import os
import sys
from configparser import ConfigParser

from yt_dlp import YoutubeDL

config = ConfigParser()
config.read('config.ini', encoding = 'utf-8')

OUT_PATH = config['PATHS']['OUT_PATH']
FFMPEG_PATH = config['PATHS']['FFMPEG_PATH']

PREEXISTING = map(lambda x: x.split('.')[0], os.listdir(OUT_PATH))

def sanitize(s: str):
    res = re.sub(r'[^\u0370-\u03ff\u1f00-\u1fffa-zA-Z0-9 ]', '', s.strip())
    ## the regular expression above matches all greek and latin characters, the digits and the space
    return ' '.join(res.split())

class SingleException(Exception):
    _message = 'Exception from Single'
    def __init__(self, m: str):
        self._message = m
    
    def __str__(self):
        return self._message

class Single():
    @staticmethod
    def set_out_path(path: str):
        global OUT_PATH, PREEXISTING
        OUT_PATH = path
        PREEXISTING = list(map(lambda x: x.split('.')[0], os.listdir(OUT_PATH)))
    
    @staticmethod
    def download(url: str, audio_only: bool = False):
        if(not os.path.isdir(OUT_PATH)):
            raise Systemsys.exit(f'Out path does not exist {OUT_PATH}')
        url = url.split('&')[0]
        try:
            with YoutubeDL() as ytdl:
                original_title = ytdl.extract_info(url, download = False).get('title', None)
        except Exception as e:
            if(__name__ == '__main__'):
                print(f'Exception: {e}')
                sys.exit(1)
            else:
                raise SingleException(f'{e}')
            
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
                
        if(title in PREEXISTING):
            if(__name__ == '__main__'):
                print('Video already downloaded.')
                sys.exit(0)
            else:
                raise SingleException('Video already downloaded.')
        ## extension = highest_res.default_filename.split('.')[1]

        ytdl_title = f"{original_title} [{url.split('/')[-1].split('&')[0][8:]}]"
        ## DOWNLOAD HIGHEST RESOLUTION
        if(not audio_only):
            ## highest_res.download(output_path = OUT_PATH, filename = video_filename)
            print('Downloading highest resolution video')
            try:
                cmd = os.system(f'yt-dlp -f bestvideo -P "{OUT_PATH}" {url}')
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
                video_filename = f'{OUT_PATH}\\{title}_video.{new_ext}'
                os.rename(f'{OUT_PATH}\\{new_file}', video_filename)
            else:
                raise SingleException()
                exit(1)
        
        print('Downloading audio')
        audio_filename = f'{title}_audio.mp4'
        try:
            ## highest_br.download(output_path = OUT_PATH, filename = audio_filename)
            ## os.system(f'yt-dlp -f bestaudio[ext=mp4] -o "{OUT_PATH}\\{audio_filename}" {url}')
            os.system(f'yt-dlp -f bestaudio -P "{OUT_PATH}" {url}')
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
        
        audio_filename = f'{OUT_PATH}\\{title}_audio.{new_ext_audio}'
        os.rename(f'{OUT_PATH}\\{new_file_audio}', audio_filename)
        
        if(not audio_only):
            print('Merging files with ffmpeg')
            if(os.path.isfile(f'{audio_filename}') and os.path.isfile(f'{video_filename}')):
                try:
                    cmd = os.system(f'{FFMPEG_PATH}\\ffmpeg -i "{video_filename}" -i "{audio_filename}" -c copy "{OUT_PATH}\\{title}.{new_ext}"')
                    if(cmd == 0):
                        os.remove(f'{video_filename}')
                        os.remove(f'{audio_filename}')
                    else:
                        raise SingleException('FFMPEG Error')
                except Exception as e:
                    if(__name__ == '__main__'):
                        print(f'Exception: {e}')
                        sys.exit(1)
                    else:
                        raise SingleException(f'{e}')
        
if(__name__ == '__main__'):
    if(len(sys.argv) != 2 and len(sys.argv) != 3):
        print('Invalid arguments')
        sys.exit(1)
    if(len(sys.argv) == 3 and sys.argv[2] != '/a'):
        print('Invalid third argument')
        sys.exit(1)
    Single.download(sys.argv[1], len(sys.argv) == 3)
