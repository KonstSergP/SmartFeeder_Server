import sqlite3
from flask import g
from ..settings.config import *



class Database():
    
    @staticmethod
    def init(app):
        log.info("Init database")
        
        app.teardown_appcontext(Database.close_connection)
        
        with app.app_context():
            db = Database.get_db()
            with app.open_resource("storage/schema.sql", mode="r") as f:
                db.cursor().executescript(f.read())
            db.commit()


    @staticmethod
    def get_db():
        log.debug("get_db")
        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = sqlite3.connect(settings.database_path)
            db.row_factory = sqlite3.Row
        return db


    @staticmethod
    def close_connection(exception):
        log.debug("close db connection")
        db = getattr(g, "_database", None)
        if db is not None:
            db.close()


    @staticmethod
    def select(query, args=(), one=False):
        log.debug("query_db")
        cur = Database.get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


    @staticmethod
    def execute(query, args=()):
        log.debug("database execute")

        db = Database.get_db()
        cur = db.cursor()
        cur.execute(query, args)
        db.commit()
