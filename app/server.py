from flask import Flask

from flask_socketio import SocketIO
from app.settings.config import *
from app.storage import Database


class Server:
    """
    Main server class.
    Handles HTTP and SocketIO communication
    """
    def __init__(self) -> None:
        """Initialize the server components."""
        self._app = Flask(__name__)
        self._server = SocketIO(self._app)


    def run(self) -> None:
        """Start the server with host and port from configuration file."""
        self._server.run(self._app, port=settings.server_port, host=settings.server_host)


    def register_http_routes(self) -> None:
        """Register HTTP routes with the Flask application."""
        import app.http_controllers   as http_controls
        self._app.register_blueprint(http_controls.routes_module)


    def register_socket_routes(self) -> None:
        """Initializes all event handlers with the current SocketIO instance."""
        import app.socket_controllers as sock_controls
        sock_controls.init_events(self._server)


    def init_db(self) -> None:
        """Initialize the database for the Flask application."""
        Database.init(self._app)


    @property
    def app(self) -> Flask:
        return self._app


def create_server() -> Server:
    """
    Function that creates and fully configures a server instance.
    Returns:
        A fully initialized Server instance ready to run
    Initialization sequence:
    1. Create a Server instance
    2. Register HTTP routes
    3. Register Socket.IO event handlers
    4. Initialize the database
    """
    server = Server()

    server.register_http_routes()
    server.register_socket_routes()
    server.init_db()

    return server
