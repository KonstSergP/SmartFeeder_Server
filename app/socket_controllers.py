from flask import request

from app.connection_handler import ConnectionHandler
from app.settings.config import *


conn_handler = ConnectionHandler()


def connection_handler():
    headers = request.headers
    conn_handler.connect(headers["type"], request.sid, headers["id"])
    log.debug(f"Connected: {headers["type"]}, {headers["id"]}, {request.sid}")


def disconnection_handler(reason):
    conn_handler.disconnect(request.sid)
    log.debug(f"Disconnected: {request.sid}, {reason}")


def stream_start_handler(data):
    try:
        conn_handler.join_stream(feeder_id=data["feeder_id"], client_sid=request.sid)
        log.debug(f"joined to stream  {data["feeder_id"]}")
        return {"success": True, "path": f"picam/{data["feeder_id"]}"}
    except:
        log.debug(f"failed to join stream from {data["feeder_id"]}", exc_info=True)
        return {"success": False}


def stream_stop_handler(data):
    try:
        conn_handler.leave_stream(feeder_id=data["feeder_id"], client_sid=request.sid)
        log.debug(f"left from stream {data["feeder_id"]}")
        return {"success": True}
    except:
        log.debug(f"failed to leave stream from {data["feeder_id"]}", exc_info=True)
        return {"success": False}


def init_events(socketio):
    socketio.on_event("connect", connection_handler)
    socketio.on_event("disconnect", disconnection_handler)
    socketio.on_event("stream start", stream_start_handler)
    socketio.on_event("stream stop", stream_stop_handler)
