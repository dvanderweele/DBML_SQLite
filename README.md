# DBML to SQLite Utility

This is a simple package built on top of [the PyDBML package by Vanderhoof](https://github.com/Vanderhoof/PyDBML). It allows you, within certain constraints, to generate valid SQLite from `.dbml` files for your Python programs.

## Installation

## Usage 

## Writing SQLite Compatible DBML

Not all valid DBML will result in valid SQLite. However, this library attempts to coerce commonly used language in DBML for other SQL flavors to compatible SQLite statements. If this is not possible, an error will be raised. 

For best results, it is recommended to stick to the following valid SQLite types, which are shown next to their corresponding Python types:

| SQLite Type | Python Type |
|     :-:     |     :-:     |
| NULL        | None        |
| INTEGER     | int         |
| REAL        | float       |
| TEXT        | str         |
| BLOB        | bytes       |

Any of the Python types above as well as any of the types in the table below, if found in your DBML, will be converted to the corresponding SQLite Type. Note the case insensitivity of the mappings; all types are uppercased for the purposes of comparison.

| Foreign Type | SQLite Type |
|      :-:     |      :-:    |
| bool         | INTEGER     |
| boolean      | INTEGER     |
| int          | INTEGER     |
| tinyint      | INTEGER     |
| smallint     | INTEGER     |
| mediumint    | INTEGER     |
| bigint       | INTEGER     |
| year         | INTEGER     |
| float        | REAL        |
| double       | REAL        |
| decimal      | REAL        |
| numeric      | REAL        |
| date         | TEXT        |
| datetime     | TEXT        |
| timestamp    | TEXT        |
| time         | TEXT        | 
| varchar      | TEXT        |
| tinytext     | TEXT        |
| mediumtext   | TEXT        |
| longtext     | TEXT        |
| tinyblob     | BLOB        |
| mediumblob   | BLOB        |
| longblob     | BLOB        |
| byte         | BLOB        |

## Enums

Enums are an aspect of SQL that is not explicitly supported in SQLite. However, it is possible to emulate the functionality in several ways. [See this stackoverflow discussion for more info](https://stackoverflow.com/questions/5299267/how-to-create-enum-type-in-sqlite#17203007).

By default, this library will emulate enums that you specify in DBML by creating a separate table. For example, given the following DBML:

```
enum message_status {
    unsent
    pending
    sent
    delivered
    failed
}

Table message {
    id integer [primary key]
    body text [not null]
    status message_status [not null]
}
```

The following SQLite will be generated:

```
CREATE TABLE message IF NOT EXISTS (
    id INTEGER PRIMARY KEY,
    body TEXT NOT NULL,
    status TEXT NOT NULL REFERENCES message_status(type)
);

CREATE TABLE message_status IF NOT EXISTS (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    seq INTEGER NOT NULL
);

INSERT INTO message_status(type, seq) VALUES ('unsent', 1);
INSERT INTO message_status(type, seq) VALUES ('pending', 2);
INSERT INTO message_status(type, seq) VALUES ('sent', 3);
INSERT INTO message_status(type, seq) VALUES ('delivered', 4);
INSERT INTO message_status(type, seq) VALUES ('failed', 5);
```

I refer to this as `full` emulation, and it is the default. The alternative is `half` emulation, and you use it as follows in your Python code:

```
from dbml_sqlite import toSQLite
output = toSQLite(dbml, emulation="half")
```

If used on the DBML above, the following SQLite is produced:

```
CREATE TABLE message IF NOT EXISTS (
    id INTEGER PRIMARY KEY,
    body TEXT NOT NULL,
    status TEXT CHECK( status IN ('unsent', 'pending', 'sent', 'delivered', 'failed') ) NOT NULL 
);
```

Note that in the case of `full` emulation, you will need to turn foreign key constraint as follows:

```
conn = sqlite3.connect("default.db")
conn.execute("PRAGMA foreign_keys = 1")
cur = conn.cursor()
```

## Testing and Coverage

After all dependencies (including development dependencies) are installed, run the tests:

```
poetry run pytest
```

Alternatively, run the tests with coverage:
```
poetry run coverage run --source dbml_sqlite -m pytest
```

View the coverage report:
```
poetry run coverage report -m
```
