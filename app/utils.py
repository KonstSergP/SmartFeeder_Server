from app.settings.config import *


def is_correct_type(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.allowed_extensions


def get_extension(filename: str) -> str:
    return filename.split('.')[-1]
