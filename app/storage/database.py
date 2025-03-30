import sqlite3
from flask import Flask
from sqlite3 import Connection
from typing import Tuple, Any, Union, Optional
from flask import g
from ..settings.config import *


class Database():
    """
    Database class that provides a simplified interface to SQLite3.
    Uses Flask's application context to manage database connections.
    """
    QueryArgs = Union[Tuple[Any, ...], Tuple[()]] # For type hinting


    @staticmethod
    def init(app: Flask) -> None:
        """
        Initialize the database
        Args:
            app: Flask application instance
        This method:
        1. Registers the close_connection function to run when app context ends
        2. Executes schema.sql
        """
        log.info("Init database")

        app.teardown_appcontext(Database.close_connection)

        with app.app_context():
            db = Database.get_db()
            with app.open_resource("storage/schema.sql", mode="r") as f:
                db.cursor().executescript(f.read())
            db.commit()


    @staticmethod
    def get_db() -> Connection:
        """
        Get a database connection
        Returns:
            conn: SQLite database connection object
        The connection is stored in Flask's g object
        """
        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = sqlite3.connect(settings.database_path)
            db.row_factory = sqlite3.Row
        return db


    @staticmethod
    def close_connection(exception: Optional[Exception]=None) -> None:
        """
        Close the database connection when the application context ends.
        Args:
            exception: Exception that might have been raised during request, may be None
        """
        db = getattr(g, "_database", None)
        if db is not None:
            db.close()


    @staticmethod
    def select(query: str, args: QueryArgs=(), one: bool=False):
        """
        Execute a SELECT query and return the results.
        Args:
            query: SQL query string
            args: Query parameters
            one: If True, returns only the first element or None
        Returns:
            Either a single row (if one=True) or a list of rows
        """
        log.debug("db_select")
        cur = Database.get_db().execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv
    
    
    @staticmethod
    def delete(query: str, args: QueryArgs=(), returning: bool=False):
        """
        Execute a DELETE query.
        Args:
            query: SQL query string
            args: Query parameters
            returning: If True, returns any values specified by RETURNING clause
        Returns:
            Query results if returning=True, otherwise None
        """
        log.debug("delete db query")
        db = Database.get_db()
        cur = db.cursor()
        cur.execute(query, args)
        db.commit()
        rv = cur.fetchall()
        if returning:
            return rv


    @staticmethod
    def execute(query: str, args: QueryArgs=()):
        """
        Execute any SQL query (typically INSERT, UPDATE, etc.).
        Commits the transaction.
        Args:
            query: SQL query string
            args: Query parameters
        """
        log.debug("db_execute")
        db = Database.get_db()
        cur = db.cursor()
        cur.execute(query, args)
        db.commit()


    @staticmethod
    def get_all_active_feeders() -> list[str]:
        feeders = Database.select("""
                              SELECT id FROM Feeders
                              WHERE session_id IS NOT NULL;
                              """)
        return [feeder["id"] for feeder in feeders]
