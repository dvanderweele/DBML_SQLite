![DBML_SQLite](https://github.com/dvanderweele/DBML_SQLite/actions/workflows/test.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/dvanderweele/DBML_SQLite/badge.svg?branch=main)](https://coveralls.io/github/dvanderweele/DBML_SQLite?branch=main)
![PyPI](https://img.shields.io/pypi/v/DBML_SQLite)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/dvanderweele/DBML_SQLite)
![PyPI -Wheel](https://img.shields.io/pypi/wheel/DBML_SQLite) 
![PyPI -Python Version](https://img.shields.io/pypi/pyversions/DBML_SQLite) 
![License -MIT](https://img.shields.io/badge/License-MIT-blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/DBML_SQLite)

# *dbml_sqlite*

This is a simple package built on top of [the PyDBML package by Vanderhoof](https://github.com/Vanderhoof/PyDBML). It allows you, within certain constraints, to generate valid SQLite from `.dbml` files for your Python programs.

## Installation

You'll need Python 3.7 or higher.

```
pip install dbml_sqlite
```

Or:

```
poetry add dbml_sqlite
```

Note that if you install the tool on your system globally with pip, you should be able to use the CLI anywhere.

## Usage

Basic use case:

```py
import sqlite3
from dbml_sqlite import toSQLite

ddl = toSQLite('dbdiagram.dbml')
con = sqlite3.connect('./example.db')
with con:
    con.executescript(ddl)
con.close()
```

Instead of directly executing the produced SQLite DDL, feel free to write it to a file instead so you can manually inspect or manipulate it. The ddl output is valid SQLite, but it is still just a Python string so you could also programmatically manipulate it or compile it further if needed.

Given a DBML file, the `toSQLite` function converts the contents to valid SQLite.

Parameters:

**dbml (str):** a valid string for converting to a Path object. Should point to a `.dbml` file containing valid DBML *or* a directory containing such files. Default is a period, in which case current working directory will be searched and all such files will be parsed.

**emulation (str):** specifies emulation mode for enum functionality since it is not directly supported by SQLite. Default is "full", and the other option is "half".

Returns:
**str:** one valid sequence of SQLite syntax.

There are other functions in the package, but they are intended for internal use only within the package. In-depth coverage of the rest of the API is at the end of this README.

## CLI

After installation, you can use the CLI from your terminal as follows:

```
dbml_sqlite [OPTIONS] SRC
```

SRC is mandatory and is the file containing dbml you want converted.

| Options | Meaning |
| :---: | :--- |
| -p, --print / -n, --no-print | Whether to print output to console.  [default: print] |
| -w, --write PATH | (Optional) File you want output written to. |
| -x, --execute PATH | (Optional) SQLite database file for executing output DDL on. Will create file if it doesn't exist. |
| -f, --full / -h, --half | Full emulation mode (separate tables) or half emulation mode (check statements) for any enums defined in your dbml. [default: full] |
| -t, --if-table-exists | (Optional) Add IF NOT EXISTS language to CREATE TABLE statements. |
| -i, --if-index-exists | (Optional) Add IF NOT EXISTS language to CREATE INDEX statements. |
| --help | Show this message and exit. |

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
    contact_id integer [not null]
}

enum zip_code {
    920
    414
    800
    900
    555
}

Table contact {
    id integer [primary key]
    name varchar(0123) [default: "Joe Smith"]
    phone mediumint [not null]
    zip zip_code [not null]

    indexes {
        (name, phone) [name: 'unique_contact', unique]
    }
}

Ref: message.contact_id > contact.id [delete: cascade, update: no action]
```

The following SQLite will be generated:

```sql
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
```

I refer to this as `full` emulation, and it is the default. The alternative is `half` emulation, and you use it as follows in your Python code:

```py
from dbml_sqlite import toSQLite
output = toSQLite('dbdiagram.dbml', emulation="half")
```

If used on the DBML above, the following SQLite is produced:

```sql
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
```

Note that in the case of `full` emulation, you will need to turn on the foreign key constraint as follows:

```py
conn = sqlite3.connect("default.db")
conn.execute("PRAGMA foreign_keys = 1")
cur = conn.cursor()
```

## Testing and Coverage

After all dependencies (including development dependencies) are installed, run the tests:

```bash
poetry run pytest
```

Alternatively, run the tests with coverage:

```bash
poetry run coverage run --source dbml_sqlite -m pytest
```

View the coverage report:

```bash
poetry run coverage report -m
```

## API

### toSQLite
    
Given a DBML file, convert contents to valid SQLite.

**Parameters:**
+ *dbml (str):* a valid string for converting to a Path object. Should point to a `.dbml` file containing valid DBML *or* a directory containing such files. Default is a period, in which case current working directory will be searched and all such files will be parsed.
+ *emulation (str):* specifies emulation mode for enum functionality since it is not directly supported by SQLite. Default is "full", and the other option is "half".
+ *tableExists (bool):* Default is True. If True, all generated `CREATE TABLE` SQLite statements will have `IF NOT EXISTS` language included.
+ *indexExists (bool):* Default is True. If True, all generated `CREATE INDEX` SQLite statements will have `IF NOT EXISTS` language included.
+ *join (bool):* Default is True. If True, function will `join` the result list of string segments with an empty string and return the resulting string to you. Otherwise, the one-dimensional list of string segments will be returned to you directly.

**Returns:**
+ *str or list of str:* a valid sequence of SQLite syntax.

### validDBMLFile
    
Return a boolean indicating whether passed string has valid `.dbml` file extension. Case-sensitive (i.e. `.DBML` not accepted).

**Parameters:**
+ *s (str):* name of file.

**Returns:**
+ *bool:* True if s ends with '.dbml', else False.

### processFile
    
Given a target `.dbml` file, parse and generate a valid SQLite string.

**Parameters:**
+ *target (Path):* File with contents to convert to SQLite.
+ *emulationMode (str):* Specifies "half" or "full" emulation for enum functionality in SQLite.
+ *tableExists (bool):* Default is True. If True, all generated `CREATE TABLE` SQLite statements will have `IF NOT EXISTS` language included.
+ *indexExists (bool):* Default is True. If True, all generated `CREATE INDEX` SQLite statements will have `IF NOT EXISTS` language included.
+ *join (bool):* Default is True. If True, function will `join` the result list of string segments with an empty string and return the resulting string to you. Otherwise, the one-dimensional list of string segments will be returned to you directly.

**Returns:**
+ *str or list of str:* valid SQLite DDL.

### processIndex

Given objects produced by the PyDBML library (or appropriately mocked), generate valid SQLite DDL for creating indexes.

**Parameters:**
+ *table (Table):* a Table object generated by the PyDBML library. This object should represent the SQLite table relevant to the index you want to create.
+ *index (Index):* an Index object generated by the PyDBML library. This object should represent the SQLite index you want to create.
+ *idxNameFunc (function):* defaults to `uuid.uuid4`. Can mock that function by passing a different function that returns a more predictable result. The result of calling this argument in either case is used as the name of an index if one is not provided for any `CREATE INDEX` statements.
+ *indexExists (bool):* Default is True. If True, the generated `CREATE INDEX` SQLite statement will have `IF NOT EXISTS` language included.
+ *join (bool):* Default is True. If True, function will `join` the result list of string segments with an empty string and return the resulting string to you. otherwise, the one-dimensional list of string segments will be returned to you directly.

**Returns:**
+ *str or list of str:* SQLite DDL for creating an index.

### processEnum

Take an Enum object generated by the PyDBML library and use it to generate SQLite DDL for creating an enum table for "full" enum emulation mode only.

**Parameters:**
+ *enum (Enum):* Enum object generated by PyDBML library representing an SQL enum.
+ *tableExists (bool):* Default is True. If True, all generated `CREATE TABLE` SQLite statements will have `IF NOT EXISTS` language included.
+ *join (bool):* Default is True. If True, function will `join` the result list of string segments with an empty string and return the resulting string to you. Otherwise, the one-dimensional list of string segments will be returned to you directly.

**Returns:**
+ *str or list of str:* SQLite DDL for creating a table to emulate SQL enum functionality.

### processTable
    
Generate SQLite DDL for creating a table.

**Parameters:**
+ *table (Table):* Table object generated by PyDBML, representing SQLite table you want to make.
+ *emulationMode (str):* if SQL enums are defined by dbml parsed by PyDBML, there are two ways to emulate them. Passing "full" for this parameter emulates enum by making a separate enum table. Passing "half" simply uses SQLite CHECK statements within column definitions utilizing enum types.
+ *tableExists (bool):* Default is True. If True, all generated `CREATE TABLE` SQLite statements will have `IF NOT EXISTS` language included.
+ *join (bool):* Default is True. If True, function will `join` the result list of string segments with an empty string and return the resulting string to you. Otherwise, the one-dimensional list of string segments will be returned to you directly.

**Return:**
+ *str or list of str:* SQLite DDL for generating a table.

### processRef
    
Convert a Ref object parsed by PyDBML from dbml into SQLite DDL.

**Parameters:**
+ *ref (Ref):* Ref object generated by PyDBML.
+ *join (bool):* Default is True. If True, function will `join` the result list of string segments with an empty string and return the resulting string to you. Otherwise, the one-dimensional list of string segments will be returned to you directly.

**Returns:**
+ *str or list of str:* SQLite DDL for defining a foreign key within a `CREATE TABLE` statement.

### processColumn

Generate SQLite DDL for creating a column.

**Parameters:**
+ *column (Column):* the Column object generated by PyDBML library.
+ *emulationMode (str):* "half" or "full" emulation of SQL enums for SQLite. The former uses `CHECK` statements within column definitions, and the latter uses separate tables.
+ *join (bool):* Default is True. If True, function will `join` the result list of string segments with an empty string and return the resulting string to you. Otherwise, the one-dimensional list of string segments will be returned to you directly.

**Returns:**
+ *str or list of str:* SQLite DDL for creating a column.

### coerceColType(colType):

Given a colType, coerce to closest native SQLite type and return that, otherwise raise a ValueError.

**Parameters:**
+ *colType (str):* column type from DBML specification.

**Returns:**
+ *str:* valid SQLite column type.

## References
+ [PyDBML by Vanderhoof](https://github.com/Vanderhoof/PyDBML)
+ [Database Markup Language — DBML](https://www.dbml.org/home/#intro)
+ [SQLite Official](https://sqlite.org/index.html)
+ [SQLite3 Python Library](https://docs.python.org/3/library/sqlite3.html)




Fri May 21 20:45:27 UTC 2021
