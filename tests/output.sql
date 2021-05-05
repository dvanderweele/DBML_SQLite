CREATE TABLE IF NOT EXISTS message (
  id INTEGER PRIMARY KEY,
  body TEXT NOT NULL,
  status TEXT CHECK( status IN ( 'unsent', 'pending', 'sent', 'delivered', 'failed' ) ) NOT NULL,
  contact_id INTEGER NOT NULL,
  FOREIGN KEY(contact_id) REFERENCES contact(id) ON UPDATE NO ACTION ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contact (
  id INTEGER PRIMARY KEY,
  name TEXT DEFAULT 'Joe Smith',
  phone INTEGER NOT NULL,
  zip TEXT CHECK( zip IN ( '920', '414', '800', '900', '555' ) ) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_contact ON contact (name, phone);