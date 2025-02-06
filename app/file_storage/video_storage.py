import os

from app.config import *


class VideoStorage:
    
    def __init__(self):
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
