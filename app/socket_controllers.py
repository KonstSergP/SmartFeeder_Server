from flask import request
from flask_socketio import emit
from app.connection_handler import ConnectionHandler
from app.settings.config import *


conn_handler = ConnectionHandler()


def connection_handler(auth):
    """Handle SocketIO connection events"""
    if "id" not in auth and "need id" in auth:
        new_id = conn_handler.generate_new_id()
        emit("assign id", {"id": new_id})
        log.debug(f"Выдан id {new_id}")
        auth["id"] = new_id

    conn_handler.connect(auth["type"], request.sid, auth["id"])
    log.debug(f"Connected: {auth["type"]}, {auth["id"]}, {request.sid}")


def disconnection_handler(reason=None):
    """Handle SocketIO disconnection events"""
    try:
        conn_handler.disconnect(request.sid)
        log.debug(f"Disconnected: {request.sid}, {reason}")
    except:
        log.debug(f"Failed to disconnect {request.sid} in connection handler", exc_info=True)


def stream_start_handler(data):
    """Handle requests to start watching a video stream."""
    try:
        conn_handler.join_stream(feeder_id=data["feeder_id"], client_sid=request.sid)
        log.debug(f"joined to stream  {data["feeder_id"]}")
        return {"success": True, "path": f"picam/{data["feeder_id"]}"}
    except:
        log.debug(f"failed to join stream from {data["feeder_id"]}", exc_info=True)
        return {"success": False}


def stream_stop_handler(data):
    """Handle requests to leave a video stream."""
    try:
        conn_handler.leave_stream(feeder_id=data["feeder_id"], client_sid=request.sid)
        log.debug(f"left from stream {data["feeder_id"]}")
        return {"success": True}
    except:
        log.debug(f"failed to leave stream from {data["feeder_id"]}", exc_info=True)
        return {"success": False}


def init_events(socketio):
    """
    Register all event handlers
    Args:
        socketio: The Flask-SocketIO instance
    """
    socketio.on_event("connect", connection_handler)
    socketio.on_event("disconnect", disconnection_handler)
    socketio.on_event("stream start", stream_start_handler)
    socketio.on_event("stream stop", stream_stop_handler)
