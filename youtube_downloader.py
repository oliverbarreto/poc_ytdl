import os
from pathlib import Path
from typing import Optional, Dict

from dotenv import load_dotenv
from loguru import logger

import yt_dlp

# Load environment variables
load_dotenv()

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    os.getenv("LOG_FILE"),
    level=os.getenv("LOG_LEVEL", "INFO"),
    rotation="10 MB",
    retention="1 week",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


class YoutubeAudioDownloader:
    def __init__(self):
        self.download_path = os.getenv("DOWNLOAD_PATH", "./downloads")
        self.audio_format = os.getenv("AUDIO_FORMAT", "m4a")

        # Create download directory if it doesn't exist
        Path(self.download_path).mkdir(parents=True, exist_ok=True)

        # Configure yt-dlp options
        self.ydl_opts = {
            "format": f"{self.audio_format}/bestaudio/best",
            "paths": {"home": self.download_path},
            "logger": logger,
            "progress_hooks": [self._progress_hook],
        }
        # Advanced options
        # self.ydl_opts = {
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        #     "format": "bestaudio/best",
        #     "paths": {"home": self.download_path},
        #     "postprocessors": [
        #         {"key": "FFmpegExtractAudio", "preferredcodec": self.audio_format}
        #     ],
        #     "logger": logger,
        #     "progress_hooks": [self._progress_hook],
        #     "extract_audio": True,
        #     "preferredcodec": "m4a",
        # }

    def extract_info(self, url: str) -> Dict:
        """
        Extract video information without downloading
        Args:
            url: YouTube URL
        Returns:
            Dict containing video information
        """
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)

                # Extract relevant information
                video_info = {
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "channel": info.get("channel"),
                    "upload_date": info.get("upload_date"),
                    "description": info.get("description"),
                    "tags": info.get("tags", []),
                    "duration": info.get("duration"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                }

                # Log video information
                logger.info(
                    f"videoID: {video_info['id']} - Title: {video_info['title']}"
                )
                # logger.info(
                #     f"[{video_info['id']}] Upload Date: {video_info['upload_date']}"
                # )
                # logger.info(
                #     f"[{video_info['id']}] Duration: {video_info['duration']} seconds"
                # )
                # logger.info(f"[{video_info['id']}] Views: {video_info['view_count']}")
                # logger.info(f"[{video_info['id']}] Likes: {video_info['like_count']}")

                return video_info

        except Exception as e:
            logger.error(f"Error extracting video information: {str(e)}")
            return {}

    def _progress_hook(self, d: dict):
        """Handle download progress updates"""

        video_id = d.get("info_dict", {}).get("id", "N/A")
        title = d.get("info_dict", {}).get("title", "N/A")

        if d["status"] == "downloading":
            try:
                progress = float(d["_percent_str"].replace("%", ""))
                logger.info(f"[{video_id}] Downloading '{title}': {progress:.1f}%")
            except:
                pass

        elif d["status"] == "finished":
            logger.info(
                f"[{video_id}] Download completed for '{title}'. Starting audio extraction..."
            )

        elif d["status"] == "error":
            logger.error(f"[{video_id}] Error downloading '{title}': {d.get('error')}")

    def download(self, url: Optional[str] = None) -> bool:
        """
        Download audio from a YouTube URL
        Args:
            url: YouTube URL. If None, uses URL from .env file
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_url = url or os.getenv("YOUTUBE_URL")
            if not target_url:
                logger.error("No URL provided")
                return False

            # First extract and display video information
            video_info = self.extract_info(target_url)
            if not video_info:
                logger.error("Failed to extract video information")
                return False

            video_id = video_info["id"]
            title = video_info["title"]
            logger.info(
                f"[{video_id}] Starting download for '{title}' from: {target_url}"
            )

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                error_code = ydl.download([target_url])

            if error_code:
                logger.error(
                    f"[{video_id}] Download failed for '{title}' with error code: {error_code}"
                )
                return False

            logger.success(
                f"[{video_id}] Download and conversion completed successfully for '{title}'"
            )
            return True

        except Exception as e:
            logger.exception(f"An error occurred: {str(e)}")
            return False


def main():
    """Main entry point"""
    try:
        downloader = YoutubeAudioDownloader()
        downloader.download()

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")

    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
