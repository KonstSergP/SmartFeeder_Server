import pytest
import sqlite3
from unittest.mock import patch, MagicMock, call
from flask import Flask, g
from app.storage.database import Database


@pytest.fixture
def app():
    """Create a Flask app fixture."""

    test_app = Flask(__name__)
    test_app.config.update({'TESTING': True})
    
    return test_app


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection."""

    mock_conn = MagicMock(spec=sqlite3.Connection)
    mock_cursor = MagicMock()
    mock_conn.execute.return_value = mock_cursor
    return mock_conn


class TestDatabase:
    """Test suite for the Database class."""

    def test_init_executes_schema(self, app, mock_db_connection):
        """Test that init executes the schema.sql file."""

        mock_cursor = mock_db_connection.cursor.return_value

        mock_file = MagicMock()
        mock_schema_content = "CREATE TABLE Test (id INTEGER PRIMARY KEY);"
        mock_file.read.return_value = mock_schema_content

        with patch.object(Database, 'get_db', return_value=mock_db_connection) as mock_get_db:
            with patch.object(app, 'open_resource', return_value=mock_file) as mock_open:

                Database.init(app)

                assert mock_open.called, "app.open_resource was not called"
                assert mock_cursor.executescript.called, "cursor.executescript was not called"
                assert mock_db_connection.commit.called, "connection.commit was not called"


    def test_init_registers_teardown(self, app):
        """Test that init registers the close_connection function."""

        with patch.object(app, 'teardown_appcontext') as mock_teardown:
            with patch.object(app, 'app_context'):
                with patch.object(Database, 'get_db'):
                    with patch.object(app, 'open_resource', return_value=MagicMock(read=MagicMock(return_value=""))):
                        Database.init(app)
                        mock_teardown.assert_called_once_with(Database.close_connection)


    def test_get_db_creates_new_connection(self, app):
        """Test that get_db creates a new connection if one doesn't exist."""

        with app.app_context():
            if hasattr(g, '_database'):
                delattr(g, '_database')
            
            with patch('sqlite3.connect') as mock_connect:
                mock_connect.return_value = MagicMock()
                db = Database.get_db()

                mock_connect.assert_called_once()
                assert db == getattr(g, '_database')


    def test_get_db_returns_existing_connection(self, app):
        """Test that get_db returns an existing connection if one exists."""

        with app.app_context():
            mock_conn = MagicMock()
            g._database = mock_conn
            
            with patch('sqlite3.connect') as mock_connect:
                db = Database.get_db()

                mock_connect.assert_not_called()
                assert db == mock_conn


    def test_close_connection_with_connection(self, app):
        """Test that close_connection closes the connection if one exists."""

        mock_conn = MagicMock()
        with app.app_context():
            with patch.object(Database, 'get_db'):
                with patch.object(app, 'open_resource', return_value=MagicMock(read=MagicMock(return_value=""))):
                    Database.init(app)
                    g._database = mock_conn

        # now close must be called
        mock_conn.close.assert_called_once()


    def test_close_connection_without_connection(self, app):
        """Test that close_connection doesn't error if no connection exists."""
        with app.app_context():
            if hasattr(g, '_database'):
                delattr(g, '_database')

            Database.close_connection(None)


    def test_select(self, app, mock_db_connection):
        """Test the select method."""

        query = "SELECT * FROM test"
        args = ("arg1", "arg2")

        mock_cursor = mock_db_connection.execute.return_value
        mock_cursor.fetchall.return_value = [{"id": 1}, {"id": 2}]
        
        with app.app_context():
            with patch.object(Database, 'get_db', return_value=mock_db_connection):
                result = Database.select(query, args)

                mock_db_connection.execute.assert_called_once_with(query, args)
                mock_cursor.fetchall.assert_called_once()
                assert result == [{"id": 1}, {"id": 2}]

                mock_db_connection.reset_mock()
                mock_cursor.reset_mock()

                mock_cursor.fetchall.return_value = [{"id": 1}, {"id": 2}]
                result = Database.select(query, args, one=True)
                
                assert result == {"id": 1}


    def test_select_empty_result(self, app, mock_db_connection):
        """Test the select method with empty result."""

        query = "SELECT * FROM test WHERE id=999"

        mock_cursor = mock_db_connection.execute.return_value
        mock_cursor.fetchall.return_value = []
        
        with app.app_context():
            with patch.object(Database, 'get_db', return_value=mock_db_connection):
                result = Database.select(query)
                assert result == []
                
                result = Database.select(query, one=True)
                assert result is None


    def test_delete(self, app, mock_db_connection):
        """Test the delete method."""

        query = "DELETE FROM test WHERE id=?"
        args = (1,)

        mock_cursor = mock_db_connection.cursor.return_value
        mock_cursor.fetchall.return_value = []

        with app.app_context():
            with patch.object(Database, 'get_db', return_value=mock_db_connection):
                result = Database.delete(query, args)

                mock_db_connection.cursor.assert_called_once()
                mock_cursor.execute.assert_called_once_with(query, args)
                mock_db_connection.commit.assert_called_once()
                assert result is None

                mock_db_connection.reset_mock()
                mock_cursor.reset_mock()

                mock_cursor.fetchall.return_value = [{"id": 1}]
                result = Database.delete(query, args, returning=True)

                assert result == [{"id": 1}]


    def test_execute(self, app, mock_db_connection):
        """Test the execute method."""

        query = "INSERT INTO test (name) VALUES (?)"
        args = ("test",)
        mock_cursor = mock_db_connection.cursor.return_value
        
        with app.app_context():
            with patch.object(Database, 'get_db', return_value=mock_db_connection):
                Database.execute(query, args)

                mock_db_connection.cursor.assert_called_once()
                mock_cursor.execute.assert_called_once_with(query, args)
                mock_db_connection.commit.assert_called_once()


    def test_get_all_active_feeders(self, app):
        """Test the get_all_active_feeders method."""

        mock_feeders = [{"id": "feeder1"}, {"id": "feeder2"}]

        with app.app_context():
            with patch.object(Database, 'select', return_value=mock_feeders) as mock_select:
                result = Database.get_all_active_feeders()

                assert result == ["feeder1", "feeder2"]
