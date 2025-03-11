from flask import Flask

from flask_socketio import SocketIO
from app.settings.config import *
from app.storage import Database


class Server:
    def __init__(self):
       self._app = Flask(__name__)
       self._server = SocketIO(self._app)


    def run(self):
        self._server.run(self._app, port=settings.server_port, host=settings.server_host)

    
    def register_http_routes(self):
        import app.http_controllers   as http_controls
        self._app.register_blueprint(http_controls.routes_module)


    def register_socket_routes(self):
        import app.socket_controllers as sock_controls
        sock_controls.init_events(self._server)

    
    def init_db(self):
        Database.init(self._app)


def create_server():
    server = Server()

    server.register_http_routes()
    server.register_socket_routes()
    server.init_db()

    return server
