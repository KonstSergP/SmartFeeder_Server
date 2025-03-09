from os import listdir, makedirs
from os.path import join, exists
from datetime import datetime
from app.utils import is_correct_type, get_extension
from flask import request
from app.settings.config import *


class VideoStorage:
    
    def __init__(self):
        if not exists(settings.upload_folder):
            makedirs(settings.upload_folder)


    def store(self, video, id):
        if not is_correct_type(video.filename):
            raise RuntimeError("Incorrect file type")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}.{get_extension(video.filename)}"

        directory = join(settings.upload_folder, id)
        if not exists(directory):
            makedirs(directory)

        video.save(join(directory, filename))
        return join(id, filename)


    def video_list(self):
        videos = []
        for directory in listdir(settings.upload_folder):
            for filename in listdir(join(settings.upload_folder, directory)):
                videos.append({
                    "filename": filename,
                    "url": f"{request.host_url}video/{join(directory, filename)}"
                })
        return videos
