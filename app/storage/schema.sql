

CREATE TABLE IF NOT EXISTS Feeders (
    id          TEXT PRIMARY KEY,
    session_id  TEXT
);

CREATE TABLE IF NOT EXISTS Clients (
    id          TEXT PRIMARY KEY,
    session_id  TEXT
);

UPDATE Feeders
SET session_id = NULL;

DELETE FROM Clients;
