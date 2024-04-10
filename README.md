Custom scripts to download videos from youtube

#### Dependencies
- Python 3
  - additionally `pytube` and `yt-dlp` (install via `pip install yt-dlp --no-deps`)
- ffmpeg installed independently

#### Usage
To download single video at best available quality: `single.py [VIDEO URL]`.

To download audio only: `single.py [VIDEO URL] /a`.

Similarly for `playlist.py`.

#### Configuration
config.ini:
```ini
[PATHS]
OUT_PATH = C:\\...
FFMPEG_PATH = C:\\...\\ffmpeg-6.1-essentials_build\\bin
```
