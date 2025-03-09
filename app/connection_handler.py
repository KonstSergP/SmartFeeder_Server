from flask_socketio import call, emit, join_room, leave_room
from app.storage import Database
from app.settings.config import *


class ConnectionHandler:
    
    def __init__(self): ...


    def connect(self, type, sid, id):
        if type == settings.feeder_type:
            Database.execute("""
                            INSERT INTO Feeders(id, session_id)
                            VALUES(?, ?)
                            ON CONFLICT(id) DO UPDATE SET
                            session_id=excluded.session_id;
                            """, (id, sid))
            
        elif type == settings.client_type:
            Database.execute("""
                            INSERT INTO Clients(id, session_id)
                            VALUES(?, ?)
                            ON CONFLICT(id) DO UPDATE SET
                            session_id=excluded.session_id;
                            """, (id, sid))
        else:
            raise ValueError(f"Unknown type: {type}")


    def disconnect(self, sid):
        feeder_id = Database.select("""
                                SELECT id FROM Feeders
                                WHERE session_id=?;
                                """, (sid,), one=True)

        if feeder_id:
            feeder_id = feeder_id[0]

            Database.delete("""
                            DELETE FROM StreamViewers
                            WHERE feeder_id=?
                            """, (feeder_id,))

            Database.execute("""
                            UPDATE Feeders
                            SET session_id=NULL
                            WHERE session_id=?
                            """, (sid,))

            emit("stream stopped", {"feeder_id": feeder_id}, to=f"stream_{feeder_id}")
            log.debug(f"Кормушка {feeder_id} отключена")


        else:
            client_id = Database.select("""
                                        SELECT id FROM Clients
                                        WHERE session_id=?;
                                        """, (sid,), one=True)

            if client_id:
                client_id = client_id[0]

                self.leave_stream(client_id=client_id, client_sid=sid)

                Database.execute("""
                                UPDATE Clients
                                SET session_id=NULL
                                WHERE session_id=?
                                """, (sid,))

                log.debug(f"Пользователь {client_id} отключен")



    def get_feeder(self, id):
        sid =   Database.select("""
                                SELECT session_id FROM Feeders
                                WHERE id=?;
                                """, (id,), one=True)
        return sid[0]


    def start_stream(self, id):
        ret = call("stream start",
                {"port": settings.rtp_port},
                to=self.get_feeder(id),
                timeout=15)
        if not ret["success"]:
            raise RuntimeError(f"{ret["Error"]} returned, \"stream started\" expected")


    def stop_stream(self, id):
        ret = call("stream stop",
                to=self.get_feeder(id),
                timeout=15)
        if not ret["success"]:
            raise RuntimeError(f"{ret["Error"]} returned, \"stream stopped\" expected")
    
    
    def join_stream(self, feeder_id, client_sid):
        viewers = Database.select("""
                                    SELECT COUNT(*) FROM StreamViewers
                                    WHERE feeder_id=?;
                                    """, (feeder_id,), one=True)[0]

        if not viewers:
            self.start_stream(feeder_id)
            log.info(f"Запущен стрим {feeder_id}")
        
        client_id = Database.select("""
                                    SELECT id FROM Clients
                                    WHERE session_id=?;
                                    """, (client_sid,), one=True)[0]
        
        Database.execute("""
                        INSERT OR IGNORE INTO StreamViewers(client_id, feeder_id)
                        VALUES(?, ?)
                        """, (client_id, feeder_id))
        
        join_room(f"stream_{feeder_id}", client_sid)
        log.debug(f"{client_id} подключился к стриму {feeder_id}")
            
    
    
    def leave_stream(self, feeder_id=None, client_id=None, client_sid=None):
        if not client_id:
            client_id = Database.select("""
                                        SELECT id FROM Clients
                                        WHERE session_id=?;
                                        """, (client_sid,), one=True)[0]
        if not feeder_id:
            feeder_id = Database.select("""
                                SELECT feeder_id FROM StreamViewers
                                WHERE client_id=?;
                                """, (client_id,), one=True)
            if feeder_id: feeder_id = feeder_id[0]

        viewers = Database.select("""
                                SELECT COUNT(*) FROM StreamViewers
                                WHERE feeder_id=? AND client_id=?;
                                """, (feeder_id, client_id), one=True)[0]
        
        if viewers > 0:
            Database.delete("""
                            DELETE FROM StreamViewers
                            WHERE feeder_id=? AND client_id=?
                            """, (feeder_id, client_id))
            log.debug(f"{client_id} покинул стрим {feeder_id}")
            leave_room(f"stream_{feeder_id}", client_sid)
            self.check_stream(feeder_id)


    def check_stream(self, feeder_id):
        viewers = Database.select("""
                                    SELECT COUNT(*) FROM StreamViewers
                                    WHERE feeder_id=?;
                                    """, (feeder_id,), one=True)[0]
        if not viewers:
            try:
                self.stop_stream(feeder_id)
                log.debug(f"Остановлен стрим {feeder_id} - нет зрителей")
            except Exception as e:
                log.debug(f"Ошибка остановки стрима {feeder_id}: {e}")
