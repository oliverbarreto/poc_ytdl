# Youtube Audio Downloader PoC

## Objetive:

We want to download the audio of a video from youtube and save it in a local folder.

## Features:

Create a python script that will download the audio of a video from youtube and save it in a local folder.

- use .env file to store the youtube video url
- use yt-dlp to download the audio of the video
- use the yt-dlp options to download the audio of the video with the best quality available
- download the audio in a local folder with the path specified in the .env file
- use logging to log the progress of the download

  - use logging to log the errors
  - use logging to log the warnings
  - use logging to log the info
  - use logging to log the debug

- Download the audio of a video from youtube and save it in a local folder.
- Download the audio of a playlist from youtube and save it in a local folder.
- Download the audio of a channel from youtube and save it in a local folder.
- Download the audio of a channel playlist from youtube and save it in a local folder.

## Tech stack - Requirements:

- Python 3.12
- yt-dlp latest version
  - https://pypi.org/project/yt-dlp/
- Loguru latest version

## YT-DLP - EMBEDDING YT-DLP

yt-dlp makes the best effort to be a good command-line program, and thus should be callable from any programming language.

Your program should avoid parsing the normal stdout since they may change in future versions. Instead, they should use options such as -J, --print, --progress-template, --exec etc to create console output that you can reliably reproduce and parse.

From a Python program, you can embed yt-dlp in a more powerful fashion, like this:

```python
from yt_dlp import YoutubeDL

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']
with YoutubeDL() as ydl:
ydl.download(URLS)
```

Most likely, you'll want to use various options. For a list of options available, have a look at yt_dlp/YoutubeDL.py or help(yt_dlp.YoutubeDL) in a Python shell. If you are already familiar with the CLI, you can use devscripts/cli_to_api.py to translate any CLI switches to YoutubeDL params.

> Tip: If you are porting your code from youtube-dl to yt-dlp, one important point to look out for is that we do not guarantee the return value of YoutubeDL.extract_info to be json serializable, or even be a dictionary. It will be dictionary-like, but if you want to ensure it is a serializable dictionary, pass it through YoutubeDL.sanitize_info as shown in the example below

### Embedding examples

#### Extracting information

```python
import json
import yt_dlp

URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'

# ℹ️ See help(yt_dlp.YoutubeDL) for a list of available options and public functions

ydl_opts = {}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
info = ydl.extract_info(URL, download=False)

    # ℹ️ ydl.sanitize_info makes the info json-serializable
    print(json.dumps(ydl.sanitize_info(info)))
```

#### Download using an info-json

```python
import yt_dlp

INFO_FILE = 'path/to/video.info.json'

with yt_dlp.YoutubeDL() as ydl:
error_code = ydl.download_with_info_file(INFO_FILE)

print('Some videos failed to download' if error_code
else 'All videos successfully downloaded')
```

#### Extract audio

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

ydl_opts = {
'format': 'm4a/bestaudio/best', # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
'postprocessors': [{ # Extract audio using ffmpeg
'key': 'FFmpegExtractAudio',
'preferredcodec': 'm4a',
}]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
error_code = ydl.download(URLS)
```

#### Filter videos

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

def longer_than_a_minute(info, \*, incomplete):
"""Download only videos longer than a minute (or with unknown duration)"""
duration = info.get('duration')
if duration and duration < 60:
return 'The video is too short'

ydl_opts = {
'match_filter': longer_than_a_minute,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
error_code = ydl.download(URLS)
```

#### Adding logger and progress hook

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

class MyLogger:
def debug(self, msg): # For compatibility with youtube-dl, both debug and info are passed into debug # You can distinguish them by the prefix '[debug] '
if msg.startswith('[debug] '):
pass
else:
self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
```

```python
def my_hook(d):

def my_hook(d):
if d['status'] == 'finished':
print('Done downloading, now post-processing ...')

ydl_opts = {
'logger': MyLogger(),
'progress_hooks': [my_hook],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
ydl.download(URLS)
```

#### Add a custom PostProcessor

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

# ℹ️ See help(yt_dlp.postprocessor.PostProcessor)

class MyCustomPP(yt_dlp.postprocessor.PostProcessor):
def run(self, info):
self.to_screen('Doing stuff')
return [], info

with yt_dlp.YoutubeDL() as ydl: # ℹ️ "when" can take any value in yt_dlp.utils.POSTPROCESS_WHEN
ydl.add_post_processor(MyCustomPP(), when='pre_process')
ydl.download(URLS)
```

#### Use a custom format selector

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

def format_selector(ctx):
""" Select the best video and the best audio that won't result in an mkv.
NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }

ydl_opts = {
'format': format_selector,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
ydl.download(URLS)
```

# Loguru

Loguru is a library that makes logging easy.

- https://pypi.org/project/loguru/
- https://loguru.readthedocs.io/en/stable/index.html
