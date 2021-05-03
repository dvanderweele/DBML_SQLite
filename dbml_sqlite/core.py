from pydbml import PyDBML, Enum
from pathlib import Path

def toSQLite(dbml=".", emulation="full"):
    """
    Given a DBML file, convert contents to valid SQLite.

    Parameters:
    dbml (str): a valid string for converting to a Path object. Should point to a `.dbml` file containing valid DBML *or* a directory containing such files. Default is a period, in which case current working directory will be searched and all such files will be parsed.
    emulation (str): specifies emulation mode for enum functionality since it is not directly supported by SQLite. Default is "full", and the other option is "half". 

    Returns: 
    str: one valid sequence of SQLite syntax.
    """
    results = []
    p = Path(dbml)
    if not p.exists():
        raise ValueError(f'Argument "{dbml}" does not refer to an existing file or directory.')
    if p.is_file():
        if validDBMLFile(dbml):
            results.append(processFile(p), emulation)
        else:
            raise ValueError(f'Argument "{dbml}" is a path to a file, but it does not have a `.dbml` extension.')
    elif p.is_dir():
        targets = [f for f in p.glob('*.dbml')]
        for target in targets:
            results.append(processFile(target), emulation)
    else:
        raise ValueError(f'Argument "{dbml}" is not a file or a directory.') 
    return " ".join(results)

def validDBMLFile(s):
    """
    Return a boolean indicating whether passed string has valid `.dbml` file extension.

    Parameters:
    s (str): name of file.

    Returns:
    bool: True if s ends with '.dbml', else False.
    """
    if s.endswith('.dbml'):
        return True
    else:
        return False

def processFile(target, emulationMode):
    """
    Given a target `.dbml` file, parse and generate a valid SQLite string.

    Parameters:
    target (Path): File with contents to convert to SQLite.
    emulationMode (str): Specifies "half" or "full" emulation for enum functionality in SQLite.

    Returns:
    str: A valid SQLite string.
    """
    parsed = PyDBML(target)
    statements = []
    for enum in parsed.enums:
        statements.append(processEnum(enum))
    for table in parsed.tables:
        statements.append(processTable(table, emulationMode))
    return " ".join(statements)

def processEnum(enum):
    segments = []
    segments.append(f'CREATE TABLE {enum.name} IF NOT EXISTS (id INTEGER PRIMARY KEY, type TEXT NOT NULL, seq INTEGER NOT NULL);')
    for i, v in enumerate(enum.items):
        segments.append(f'INSERT INTO {enum.name}(type, seq) VALUES ({v.name}, {i + 1});')
    return " ".join(segments)

def processTable(table, emulationMode):
    segments = []
    segments.append(f'CREATE TABLE {table.name} IF NOT EXISTS (')
    for col in table.columns:
        segments.append(processColumn(col), emulationMode)
    segments.append(');')
    return "".join(segments)

def processColumn(column, emulationMode):
    segments = []
    segments.append(column.name)
    if isinstance(column.type, str):
        segments.append(column.type)
        # column constraints
    elif isinstance(column.type, Enum):
        if emulationMode == 'full':
            segments.append(f'TEXT NOT NULL REFERENCES {column.type.name}(type)')
        else:
            segments.append(f'TEXT CHECK( {column.name} IN (')
            enums = []
            for e in column.type.items:
                enums.append(f"'{e.name}'")
            segments.append(", ".join(enums))
            segments.append(') NOT NULL')
    else:
        raise ValueError('Data type of column specification unknown.')
    return "".join(segments)

def coerceColType(colType):
    """ 
    Given a colType, coerce to closest native SQLite type and return that, otherwise raise a ValueError.

    Parameters:
    colType (str): column type from DBML specification.

    Returns:
    str: valid SQLite column type. 
    """
    colType = colType.upper()
    nativeTypes = ('NULL', 'INTEGER', 'REAL', 'TEXT', 'BLOB')
    if colType in nativeTypes:
        return colType
    integers = ('BOOL', 'BOOLEAN', 'INT', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'LONGINT', 'BIGINT', 'YEAR')
    if colType in integers:
        return 'INTEGER'
    reals = ('FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC')
    if colType in reals:
        return 'REAL'
    texts = ('DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'VARCHAR', 'TINYTEXT', 'SMALLTEXT', 'MEDIUMTEXT', 'LONGTEXT')
    if colType in texts:
        return 'TEXT'
    blobs = ('TINYBLOB', 'SMALLBLOB', 'MEDIUMBLOB', 'LONGBLOB', 'BYTE', 'BYTES')
    if colType in blobs:
        return 'BLOB'
    raise ValueError(f'Could not figure out how to coerce "{colType}" to valid SQLite type.')
