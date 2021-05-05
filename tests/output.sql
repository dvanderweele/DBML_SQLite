CREATE TABLE IF NOT EXISTS message_status (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL UNIQUE,
  seq INTEGER NOT NULL UNIQUE
);
INSERT INTO message_status(type, seq) VALUES ('unsent', 1);
INSERT INTO message_status(type, seq) VALUES ('pending', 2);
INSERT INTO message_status(type, seq) VALUES ('sent', 3);
INSERT INTO message_status(type, seq) VALUES ('delivered', 4);
INSERT INTO message_status(type, seq) VALUES ('failed', 5);

CREATE TABLE IF NOT EXISTS zip_code (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL UNIQUE,
  seq INTEGER NOT NULL UNIQUE
);
INSERT INTO zip_code(type, seq) VALUES ('920', 1);
INSERT INTO zip_code(type, seq) VALUES ('414', 2);
INSERT INTO zip_code(type, seq) VALUES ('800', 3);
INSERT INTO zip_code(type, seq) VALUES ('900', 4);
INSERT INTO zip_code(type, seq) VALUES ('555', 5);

CREATE TABLE IF NOT EXISTS message (
  id INTEGER PRIMARY KEY,
  body TEXT NOT NULL,
  status TEXT NOT NULL REFERENCES message_status(type),
  contact_id INTEGER NOT NULL,
  FOREIGN KEY(contact_id) REFERENCES contact(id) ON UPDATE NO ACTION ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contact (
  id INTEGER PRIMARY KEY,
  name TEXT DEFAULT 'Joe Smith',
  phone INTEGER NOT NULL,
  zip TEXT NOT NULL REFERENCES zip_code(type)
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_contact ON contact (name, phone);