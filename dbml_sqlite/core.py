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
            results.append(processFile(p))
        else:
            raise ValueError(f'Argument "{dbml}" is a path to a file, but it does not have a `.dbml` extension.')
    elif p.is_dir():
        targets = [f for f in p.glob('*.dbml')]
        for target in targets:
            results.append(processFile(target))
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

def processFile(target):
    """
    Given a target `.dbml` file, parse and generate a valid SQLite string.

    Parameters:
    target (Path): File with contents to convert to SQLite.

    Returns:
    str: A valid SQLite string.
    """
    parsed = PyDBML(target)
    statements = []
    for table in parsed.tables:
        statements.append(processTable(table))
    return " ".join(statements)

def processTable(table):
    segments = []
    segments.append(f'CREATE TABLE {table.name} IF NOT EXISTS (')
    for col in table.columns:
        segments.append(processColumn(col))
    segments.append(');')
    return "".join(segments)

def processColumn(column):
    if isinstance(column.type, str):
        pass
    elif isinstance(column.type, Enum):
        pass
    else:
        raise Error('Data type of column specification unknown.')

def coerceColType(colType):
    pass
