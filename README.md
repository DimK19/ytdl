A convenient wrapper of [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) for downloading youtube videos and playlists from the command line.

#### Dependencies
- Python 3
  - additionally `yt-dlp` (install via `pip install yt-dlp --no-deps`)
- ffmpeg installed independently
- Mozilla Firefox (specifically for downloading members-only videos)

#### Configuration
config.ini:
```ini
[PATHS]
OUT_PATH = C:\\...
FFMPEG_PATH = C:\\...\\ffmpeg-6.1-essentials_build\\bin
```
#### Usage
To download a single video at the best available quality: `single.py -u [VIDEO URL]`. Optional flags for `single.py`:
- `--audio-only`
- `--premium`: for members-only videos. **Currently, this works by getting the cookies from firefox. In this case, video title and channel name cannot be extracted automatically**. They must be defined manually within the code: see the command below for channel name, and see the code to create the necessary `premiumTitles.txt` file.
- `--res`: The video resolution **height** in pixels.
- `--cn`: The name of the channel publishing the video.

Similarly for `playlist.py`. In addition to the arguments above, playlist also supports:
- `--skip`: number of items to skip in the playlist before starting download.
- `--stop`: stop downloading after this many playlist items.

_Issues are often resolved by updating to the latest version of `yt-dlp`._
