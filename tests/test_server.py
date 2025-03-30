import pytest
from unittest.mock import patch, MagicMock
from app.server import create_server, Server
from app.settings.config import settings

class TestServer:

    def test_server_creation(self):
        """Test that the server can be created and configured correctly."""

        with patch.object(Server, 'register_http_routes') as mock_http:
            with patch.object(Server, 'register_socket_routes') as mock_socket:
                with patch.object(Server, 'init_db') as mock_db:
                    server = create_server()

                    mock_http.assert_called_once()
                    mock_socket.assert_called_once()
                    mock_db.assert_called_once()

                    assert server is not None
                    assert server.app is not None
