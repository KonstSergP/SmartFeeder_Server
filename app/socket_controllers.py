from flask import request

from app.config import *

def connection_handler(data):
    print(data)
    print(request.sid)
    print("Hello")


def disconnection_handler(reason):
    print(reason)
    print("Bye")


def init_events(socketio):
    socketio.on_event('connect', connection_handler)
    socketio.on_event('disconnect', disconnection_handler)
