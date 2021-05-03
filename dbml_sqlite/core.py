from pydbml import PyDBML
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
    p = Path(dbml)
    if p.is_file():
        pass
    elif p.is_dir():
        pass
    else:
        pass
    return dbml 

def validDBMLFile(s):
    """
    Return a boolean indicating whether passed string has valid `.dbml` file extension.

    Parameters:
    s (str): name of file.

    Returns:
    bool: True if s ends with '.dbml' or '.DBML', else False.
    """
    if s.lower().endswith('.dbml'):
        return True
    else:
        return False
