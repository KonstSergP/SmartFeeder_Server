from app.settings.config import *


def is_correct_type(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.allowed_extensions
