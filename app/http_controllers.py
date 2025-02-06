from flask import request, send_from_directory, jsonify, Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app.file_storage import video_storage
from app.config import *
from app.utils import is_correct_filename



routes_module = Blueprint("routes", __name__)


@routes_module.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if is_correct_filename(video.filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"video_{timestamp}_{secure_filename(video.filename)}"
        video.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        return jsonify({'message': 'Video uploaded successfully', 'filename': filename}), 200
    
    return jsonify({'error': 'Invalid file'}), 400


@routes_module.route('/videos', methods=['GET'])
def list_videos():
    videos = []
    for filename in os.listdir(Config.UPLOAD_FOLDER):
        if is_correct_filename(filename): # is it necessary?
            videos.append({
                'filename': filename,
                'url': f'/video/{filename}'
            })
    return jsonify(videos)


@routes_module.route('/video/<filename>', methods=['GET'])
def get_video(filename):
    try:
        return send_from_directory(f"../{Config.UPLOAD_FOLDER}", filename)
    except FileNotFoundError:
        return jsonify({'error': 'Video not found'}), 404
