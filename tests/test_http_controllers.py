import pytest
import json
import io
from unittest.mock import patch, MagicMock
from app.server import create_server
from app.storage import video_storage, Database
from app.settings.config import settings


@pytest.fixture
def client():
    """Create a test client for the Flask app."""

    server = create_server()
    app = server.app
    app.config.update({'TESTING': True})

    with patch.object(Database, 'init'):
        return app.test_client()


class TestHTTPControllers:
    """Test suite for HTTP endpoints."""

    def test_list_feeders(self, client):
        """Test the /feeders route."""

        mock_feeders = ["feeder1", "feeder2"]

        with patch.object(Database, 'get_all_active_feeders', return_value=mock_feeders):
            response = client.get('/feeders')

            assert response.status_code == 200
            assert json.loads(response.data) == mock_feeders


    def test_list_videos(self, client):
        """Test the /videos endpoint."""

        mock_videos = [
            {"filename": "video1.mp4", "url": "http://localhost/video/feeder1/video1.mp4"},
            {"filename": "video2.mp4", "url": "http://localhost/video/feeder2/video2.mp4"}
        ]

        with patch.object(video_storage, 'video_list', return_value=mock_videos):
            response = client.get('/videos')

            assert response.status_code == 200
            assert json.loads(response.data) == mock_videos


    def test_upload_video_success(self, client):
        """Test successful video upload."""

        mock_file = io.BytesIO(b"fake video content")
        mock_feeder_id = "test_feeder"
        mock_path = f"{mock_feeder_id}/video_test_test.mp4"

        with patch.object(video_storage, 'store', return_value=mock_path):
            response = client.post('/upload',
                                data={
                                    'video': (mock_file, 'test.mp4'), # file like tuple converts into FileStorage
                                    'id': mock_feeder_id})

            assert response.status_code == 200
            result = json.loads(response.data)
            assert "message" in result
            assert "path" in result
            assert result["path"] == mock_path


    def test_upload_video_no_file(self, client):
        """Test video upload without a file."""

        response = client.post('/upload', data={})
        
        assert response.status_code == 400
        assert json.loads(response.data)["error"] == "No video file"


    def test_upload_video_empty_filename(self, client):
        """Test video upload with empty filename."""

        mock_file = io.BytesIO(b"")
        
        response = client.post('/upload',
                            data={
                                'video': (mock_file, ''),
                                'id': 'feeder123'})

        assert response.status_code == 400
        assert json.loads(response.data)["error"] == "No selected file"


    def test_get_video_success(self, client):
        """Test getting a specific video."""

        video_path = "feeder1/test_video.mp4"

        with patch('app.http_controllers.send_from_directory', return_value="video content") as mock_send:
            response = client.get(f'/video/{video_path}')
            print(response)
            mock_send.assert_called_once()
            assert "video content" == response.get_data(as_text=True)


    def test_get_video_not_found(self, client):
        """Test getting a non-existent video."""

        video_path = "feeder1/nonexistent.mp4"

        with patch('app.http_controllers.send_from_directory', side_effect=FileNotFoundError):
            response = client.get(f'/video/{video_path}')

            assert response.status_code == 404
            assert json.loads(response.data)["error"] == "Video not found"
