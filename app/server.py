from flask import Flask

from app.socket_server import SocketServer
from app.config import *

class Server:
    def __init__(self):
       self._app = Flask(__name__)
       self._server = SocketServer(self._app)

    def run(self):
        self._server.run(self._app, port=5000, host="0.0.0.0")
    
    def register_http_routes(self):
        import app.http_controllers   as http_controls
        self._app.register_blueprint(http_controls.routes_module)

    def register_socket_routes(self):
        import app.socket_controllers as sock_controls
        sock_controls.init_events(self._server)
