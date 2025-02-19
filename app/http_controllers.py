from flask import request, send_from_directory, jsonify, Blueprint

from app.storage import video_storage
from app.settings.config import *


routes_module = Blueprint("routes", __name__)


@routes_module.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file"}), 400

    video = request.files["video"]
    if video.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        video_url = video_storage.store(video, request.headers["id"])
        return jsonify({"message": "Video uploaded successfully", "url": video_url}), 200
    except:
        return jsonify({"error": "Invalid file"}), 400


@routes_module.route("/videos", methods=["GET"])
def list_videos():
    videos = video_storage.video_list()
    return jsonify(videos), 200


@routes_module.route(f"/{settings.upload_folder}/<path:subpath>", methods=["GET"])
def get_video(subpath):
    try:
        return send_from_directory(f"../{settings.upload_folder}", subpath)
    except FileNotFoundError:
        return jsonify({"error": "Video not found"}), 404
