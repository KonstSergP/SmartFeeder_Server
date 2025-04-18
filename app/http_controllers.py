from flask import request, send_from_directory, jsonify, Blueprint
from os.path import join
from app.storage import video_storage, Database
from app.settings.config import *


routes_module = Blueprint("routes", __name__)


@routes_module.route("/upload", methods=["POST"])
def upload_video():
    """
    Handle video upload requests from feeders.

    Expects:
    - 'video' file to be stored on server
    - 'id' containing the feeder identifier
    """
    if "video" not in request.files:
        return jsonify({"error": "No video file"}), 400

    video = request.files["video"]
    if video.filename == "":
        log.debug("No file")
        return jsonify({"error": "No selected file"}), 400
    try:
        id = request.form.to_dict(flat=True)["id"]
        video_path = video_storage.store(video, id)
        log.debug(f"Uploaded successfully, id={id}")
        return jsonify({"message": "Video uploaded successfully", "path": video_path}), 200
    except:
        log.debug("Invalid file", exc_info=True)
        return jsonify({"error": "Invalid file"}), 400


@routes_module.route("/videos", methods=["GET"])
def list_videos():
    """
    Get list of all available videos.
    Returns list of dicts in format {filename : ... , url : full url to video}
    """
    videos = video_storage.video_list()
    log.debug("Returning video list")
    return jsonify(videos), 200


@routes_module.route(f"/video/<path:subpath>", methods=["GET"])
def get_video(subpath):
    """Get a specific video file."""
    try:
        log.debug(f"sending video {subpath}")
        return send_from_directory(join("..", f"{settings.upload_folder}"), subpath)
    except FileNotFoundError:
        log.error(f"not found file {subpath}")
        return jsonify({"error": "Video not found"}), 404


@routes_module.route("/feeders", methods=["GET"])
def list_feeders():
    """Get list of all connected feeders."""
    feeders = Database.get_all_active_feeders()
    log.debug(f"Returning connected feeders list: {len(feeders)} feeders")
    return jsonify(feeders), 200
