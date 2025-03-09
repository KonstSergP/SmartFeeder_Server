from flask import request, send_from_directory, jsonify, Blueprint
from os.path import join
from app.storage import video_storage
from app.settings.config import *


routes_module = Blueprint("routes", __name__)


@routes_module.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file"}), 400

    video = request.files["video"]
    if video.filename == "":
        log.debug("No file")
        return jsonify({"error": "No selected file"}), 400

    try:
        video_path = video_storage.store(video, request.headers["id"])
        log.debug("Uploaded successfully")
        return jsonify({"message": "Video uploaded successfully", "path": video_path}), 200
    except:
        log.debug("Invalid file", exc_info=True)
        return jsonify({"error": "Invalid file"}), 400


@routes_module.route("/videos", methods=["GET"])
def list_videos():
    videos = video_storage.video_list()
    return jsonify(videos), 200


@routes_module.route(f"/video/<path:subpath>", methods=["GET"])
def get_video(subpath):
    try:
        return send_from_directory(join("..", f"{settings.upload_folder}"), subpath)
    except FileNotFoundError:
        return jsonify({"error": "Video not found"}), 404
