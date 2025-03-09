

CREATE TABLE IF NOT EXISTS Feeders (
    id          TEXT PRIMARY KEY,
    session_id  TEXT
);


CREATE TABLE IF NOT EXISTS Clients (
    id          TEXT PRIMARY KEY,
    session_id  TEXT
);


CREATE TABLE IF NOT EXISTS StreamViewers (
    client_id   TEXT,
    feeder_id   TEXT,
    PRIMARY KEY (client_id, feeder_id),
    FOREIGN KEY (client_id) REFERENCES Clients(id),
    FOREIGN KEY (feeder_id) REFERENCES Feeders(id)
);


UPDATE Feeders
SET session_id = NULL;

UPDATE Clients
SET session_id = NULL;

DELETE FROM StreamViewers;
