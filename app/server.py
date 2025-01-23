from flask import Flask
from flask_socketio import SocketIO

from app.config import *

class Server:
    def __init__(self):
       self.app = Flask(__name__)
       self.socket = SocketIO(self.app)
    
    def run(self):
        self.socket.run(self.app, port=5000, host="0.0.0.0")
