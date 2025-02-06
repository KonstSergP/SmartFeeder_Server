from flask import request

from flask_socketio import call
from app.socket_server import SocketServer
from app.config import *

feeder = None


def connection_handler():
    global feeder
    headers = request.headers
    if "id" in headers:
        print(headers["id"])
        feeder = request.sid



def disconnection_handler(reason):
    print(reason)
    print("Bye")


def stream_start_handler():
    if feeder:
        call("stream start", to=feeder)


def stream_end_handler():
    if feeder:
        call("stream end", to=feeder)


def init_events(socketio):
    socketio.on_event('connect', connection_handler)
    socketio.on_event('disconnect', disconnection_handler)
    socketio.on_event('stream start', stream_start_handler)
    socketio.on_event('stream end', stream_end_handler)
