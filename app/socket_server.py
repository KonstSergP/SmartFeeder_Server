from flask_socketio import SocketIO

from app.utils import Singleton


class SocketServer(SocketIO, metaclass=Singleton):
    pass
