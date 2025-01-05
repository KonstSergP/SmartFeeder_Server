from app.server import Server
from app.config import *
import os


if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)


def create_server():
    server = Server()

    import app.controllers as controls

    server.app.register_blueprint(controls.routes_module)
    
    return server
