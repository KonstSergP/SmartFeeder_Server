from os import listdir, makedirs
from os.path import join, exists
from datetime import datetime
from app.utils import is_correct_type
from app.settings.config import *


class VideoStorage:
    
    def __init__(self):
        if not exists(settings.upload_folder):
            makedirs(settings.upload_folder)


    def store(video, id):
        if is_correct_type(video.filename):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}"
            
            directory = join(settings.upload_folder, id)
            if not exists(directory):
                makedirs(directory)
            
            path = join(directory, filename)
            video.save(path)
            return path
        raise RuntimeError("Incorrect file type")


    def video_list():  
        videos = []
        for filename in listdir(settings.upload_folder):
                videos.append({
                    "filename": filename,
                    "url": f"/{join(settings.upload_folder, filename)}"
                })
        return videos
