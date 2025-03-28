from os import listdir, makedirs
from os.path import join, exists
from datetime import datetime
from app.utils import is_correct_type, get_extension
from typing import List
from flask import request
from werkzeug.datastructures import FileStorage
from app.settings.config import *


class VideoStorage:
    """
    Manages storage of video files.
    Videos are stored in specific folders inside the configured upload directory.
    """

    def __init__(self) -> None:
        """
        Initialize the video storage.
        Creates the upload folder if it doesn't exist.
        """
        if not exists(settings.upload_folder):
            makedirs(settings.upload_folder)


    def store(self, video: FileStorage, id: str) -> str:
        """
        Store a video file from feeder 'id'.
        Args:
            video: The uploaded video file object
            id: Feeder identifier
        Returns:
            Relative path to the stored video file from upload folder
        """
        # Validate the video file type
        if not is_correct_type(video.filename):
            raise RuntimeError("Incorrect file type")

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}.{get_extension(video.filename)}"

        directory = join(settings.upload_folder, id)
        if not exists(directory):
            makedirs(directory)

        video.save(join(directory, filename))
        return join(id, filename)


    def video_list(self) -> List[dict]:
        """
        Generate a list of all stored videos
        Returns:
            List of dictionaries containing filename and full URL for each video
            Format: [{"filename": str, "url": str}, ...]
        """
        videos = []
        # Iterate through all device folders
        for directory in listdir(settings.upload_folder):
            # Iterate through all files in each folder
            for filename in listdir(join(settings.upload_folder, directory)):
                videos.append({
                    "filename": filename,
                    "url": f"{request.host_url}video/{join(directory, filename)}"
                })
        return videos
