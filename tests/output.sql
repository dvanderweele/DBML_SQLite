CREATE TABLE message_status IF NOT EXISTS (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL UNIQUE,
  seq INTEGER NOT NULL UNIQUE
);
INSERT INTO message_status(type, seq) VALUES ('unsent', 1);
INSERT INTO message_status(type, seq) VALUES ('pending', 2);
INSERT INTO message_status(type, seq) VALUES ('sent', 3);
INSERT INTO message_status(type, seq) VALUES ('delivered', 4);
INSERT INTO message_status(type, seq) VALUES ('failed', 5);

CREATE TABLE message IF NOT EXISTS (,
  id INTEGER PRIMARY KEY,
  body TEXT NOT NULL,
  status TEXT NOT NULL REFERENCES message_status(type)
);