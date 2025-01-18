<div align="center">
  <a href="https://oliverbarreto.com">
    <img src="https://www.oliverbarreto.com/images/site-logo.png" />
  </a>
</div>
</br>
</br>
<div align="center">
  <h1>Proof of Concept - Youtube Audio Downloader</h1>
  <strong>Proof of Concept - Youtube Audio Downloader</strong>
  </br>
  </br>
  <p>Created with ❤️ by Oliver Barreto</p>
</div>

</br>
</br>

# Proof of Concept - Youtube Audio Downloader

## Objetive

We want to download the audio of a video from youtube and save it in a local folder.

This is a classic script, but this time, we are testing a new library called YT-DLP

- Official Github Repository: https://github.com/yt-dlp/yt-dlp
- Docs: https://pypi.org/project/yt-dlp/#embedding-examples

## Features

- use .env file to store the youtube video url
- use yt-dlp to download the audio of the video
- use the yt-dlp options to download the audio of the video with the best quality available
- download the audio in a local folder with the path specified in the .env file
- use logging to log the progress of the download and errors
