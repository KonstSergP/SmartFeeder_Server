import pytest
from unittest.mock import patch, MagicMock, call
from flask import Flask
from flask_socketio import SocketIO
from app.socket_controllers import connection_handler, disconnection_handler, stream_start_handler, stream_stop_handler
from app.connection_handler import ConnectionHandler
from app.settings.config import settings


@pytest.fixture
def app():
    """Create a Flask app fixture."""

    test_app = Flask(__name__)
    test_app.config.update({'TESTING': True})
    return test_app


@pytest.fixture
def socketio(app):
    """Create a Flask-SocketIO fixture."""
    return SocketIO(app)


class TestSocketControllers:
    """Test suite for Socket.IO controllers."""

    def test_connection_handler_new_id(self, request, app, socketio):
        """Test connection handler with new ID request."""

        with app.test_request_context('/'):
            with patch('app.socket_controllers.emit') as mock_emit:
                with patch.object(ConnectionHandler, 'generate_new_id', return_value='new_test_id'):
                    with patch.object(ConnectionHandler, 'connect') as mock_connect:
                        with patch('app.socket_controllers.request') as mock_request:
                            mock_request.sid = "TEST"
                            connection_handler({"need id": True, "type": "client"})

                            mock_emit.assert_called_once_with("assign id", {"id": "new_test_id"})
                            mock_connect.assert_called_once_with("client", "TEST", "new_test_id")


    def test_connection_handler_existing_id(self, app, socketio):
        """Test connection handler with existing ID."""

        with app.test_request_context('/'):
            with patch.object(ConnectionHandler, 'connect') as mock_connect:
                with patch('app.socket_controllers.request') as mock_request:
                    mock_request.sid = "TEST"
                    connection_handler({"id": "existing-id", "type": "feeder"})

                    mock_connect.assert_called_once_with("feeder", "TEST", "existing-id")


    def test_disconnection_handler(self, app, socketio):
        """Test disconnection handler."""

        with app.test_request_context('/'):
            with patch.object(ConnectionHandler, 'disconnect') as mock_disconnect:
                with patch('app.socket_controllers.request') as mock_request:
                    mock_request.sid = "TEST"
                    disconnection_handler("test reason")

                    mock_disconnect.assert_called_once_with("TEST")


    def test_stream_start_handler_success(self, app, socketio):
        """Test stream start handler - successful case."""

        with app.test_request_context('/'):
            with patch.object(ConnectionHandler, 'join_stream') as mock_join:
                with patch('app.socket_controllers.request') as mock_request:
                    mock_request.sid = "TEST"
                    result = stream_start_handler({"feeder_id": "feeder_test"})

                    mock_join.assert_called_once_with(feeder_id="feeder_test", client_sid="TEST")
                    assert result["success"] is True
                    assert result["path"] == "picam/feeder_test"


    def test_stream_start_handler_failure(self, app, socketio):
        """Test stream start handler - failure case."""

        with app.test_request_context('/'):
            with patch.object(ConnectionHandler, 'join_stream', side_effect=Exception("Test error")):
                result = stream_start_handler({"feeder_id": "feeder_test"})

                assert result["success"] is False


    def test_stream_stop_handler_success(self, app, socketio):
        """Test stream stop handler - successful case."""

        with app.test_request_context('/'):
            with patch.object(ConnectionHandler, 'leave_stream') as mock_leave:
                with patch('app.socket_controllers.request') as mock_request:
                    mock_request.sid = "TEST"
                    result = stream_stop_handler({"feeder_id": "feeder_test"})
                    
                    mock_leave.assert_called_once_with(feeder_id="feeder_test", client_sid="TEST")
                    assert result["success"] is True


    def test_stream_stop_handler_failure(self, app, socketio):
        """Test stream stop handler - failure case."""
        with app.test_request_context('/'):
            with patch.object(ConnectionHandler, 'leave_stream', side_effect=Exception("Test error")):
                result = stream_stop_handler({"feeder_id": "feeder_test"})

                assert result["success"] is False
