from flask_socketio import call, emit, join_room, leave_room
from app.storage import Database
import uuid
from typing import Optional
from app.settings.config import *


class ConnectionHandler:
    """
    Manages the connections of feeders and clients.
    This class handles:
    - Connection and disconnection of feeders and clients
    - Stream management (starting/stopping video streams)
    - Viewer management (joining/leaving streams)
    - Room-based communication
    """

    def __init__(self): ...


    def connect(self, type: str, sid: str, id: str) -> None:
        """
        Register a new connection in the database.
        Args:
            type: The connection type ('feeder' or 'client')
            sid: The SocketIO session ID
            id: The unique identifier for the feeder or client
        """
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


    def disconnect(self, sid: str) -> None:
        """
        Handle a disconnection event by cleaning up database entries.
        For feeders: Removes all stream viewers
        For clients: Removes them from any streams they were viewing
        Args:
            sid: The SocketIO session ID being disconnected
        """
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



    def get_feeder(self, id: str) -> str:
        """Get the session ID for a feeder by its unique identifier."""
        sid =   Database.select("""
                                SELECT session_id FROM Feeders
                                WHERE id=?;
                                """, (id,), one=True)
        return sid[0]


    def start_stream(self, id: str) -> None:
        """Request a feeder to start streaming video."""
        ret = call("stream start",
                {"port": settings.rtp_port},
                to=self.get_feeder(id),
                timeout=15)
        if not ret["success"]:
            raise RuntimeError(f"{ret["Error"]} returned, \"stream started\" expected")


    def stop_stream(self, id: str) -> None:
        """Request a feeder to stop streaming video."""
        ret = call("stream stop",
                to=self.get_feeder(id),
                timeout=15)
        if not ret["success"]:
            raise RuntimeError(f"{ret["Error"]} returned, \"stream stopped\" expected")


    def join_stream(self, feeder_id: str, client_sid: str) -> None:
        """
        Add a client to a feeder's video stream.
        If this is the first viewer, the stream will be started automatically.
        Args:
            feeder_id: The feeder's unique identifier
            client_sid: The client's Socket.IO session ID
        """
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


    def leave_stream(self, feeder_id: Optional[str]=None, client_id: Optional[str]=None, client_sid: Optional[str]=None) -> None:
        """
        Remove a client from a feeder's video stream.
        Must be called with either client id or client session id,
        and feeder id is optional
        """
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


    def check_stream(self, feeder_id: str) -> None:
        """
        Check if a stream has any viewers and stop it if none.
        This function is called to determine if the stream should be stopped.
        """
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


    def generate_new_id(self) -> str:
        """Generate new unique identifier"""
        return str(uuid.uuid4())
