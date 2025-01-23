from app.server import Server
from app.config import *
import os


if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)


def create_server():
    server = Server()

    import app.http_controllers   as http_controls
    import app.socket_controllers as sock_controls

    server.app.register_blueprint(http_controls.routes_module)
    sock_controls.init_events(server.socket)
    
    return server
