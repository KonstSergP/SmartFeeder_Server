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
        conn_handler.start_stream(data["id"])
        log.debug(f"started stream from {data["id"]}")
        return "stream started"
    except:
        log.debug(f"failed to start stream from {data["id"]}")
        return "failed to start stream"


def stream_stop_handler(data):
    try:
        conn_handler.stop_stream(data["id"])
        log.debug(f"stopped stream from {data["id"]}")
        return "stream stopped"
    except:
        log.debug(f"failed to stop stream from {data["id"]}")
        return "failed to stop stream"


def init_events(socketio):
    socketio.on_event("connect", connection_handler)
    socketio.on_event("disconnect", disconnection_handler)
    socketio.on_event("stream start", stream_start_handler)
    socketio.on_event("stream stop", stream_stop_handler)
