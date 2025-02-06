from app.server import Server
from app.config import *


def create_server():
    server = Server()

    server.register_http_routes()
    server.register_socket_routes()
    
    return server
