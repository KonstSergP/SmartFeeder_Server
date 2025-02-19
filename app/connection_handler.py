from flask_socketio import call
from app.storage import Database
from app.settings.config import *


class ConnectionHandler:
    
    def __init__(self): ...


    def connect(self, type, sid, id):
        if type == "feeder":
            Database.execute("""
                            INSERT INTO Feeders(id, session_id)
                            VALUES(?, ?)
                            ON CONFLICT(id) DO UPDATE SET
                            session_id=excluded.session_id;
                            """, (id, sid))
        else:
            Database.execute("""
                            INSERT INTO Clients(id, session_id)
                            VALUES(?, ?)
                            ON CONFLICT(id) DO UPDATE SET
                            session_id=excluded.session_id;
                            """, (id, sid))


    def disconnect(self, sid):
        id =    Database.select("""
                                SELECT id FROM Feeders
                                WHERE session_id=?;
                                """, (sid,), one=True)

        if id:
            Database.execute("""
                             UPDATE Feeders
                             SET session_id=NULL
                             WHERE session_id=?
                             """, (sid,))
        else:
            Database.execute("""
                             DELETE FROM Clients
                             WHERE session_id=?
                             """, (sid,))


    def get_feeder(self, id):
        sid =   Database.select("""
                                SELECT session_id FROM Feeders
                                WHERE id=?;
                                """, (id,), one=True)
        return sid


    def start_stream(self, id):
        ret = call("stream start", 
                {"port": settings.rtp_port, "path": settings.rtp_path},
                to=self.get_feeder(id),
                timeout=15)
        if ret != "stream started":
            raise RuntimeError(f"{ret} returned, \"stream started\" expected")


    def stop_stream(self, id):
        ret = call("stream stop",
                to=self.get_feeder(id),
                timeout=15)
        if ret != "stream stopped":
            raise RuntimeError(f"{ret} returned, \"stream stopped\" expected")
