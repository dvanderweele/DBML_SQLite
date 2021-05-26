import pytest
import os
import sqlite3
from dbml_sqlite import __version__
from dbml_sqlite import toSQLite, validDBMLFile, coerceColType, processColumn, processRef, processEnum, processTable, processFile, processIndex
from pydbml.classes import Enum
from pathlib import Path

def MockNameFunc():
    return 'mockname'
class MockEnum(Enum):
    def __init__(self, name, items):
        self.name = name
        self.items = items
class MockItem:
    def __init__(self, name):
        self.name = name
class MockColumn:
    def __init__(self, name, Type, pk, not_null, unique, default):
        self.name = name
        self.type = Type
        self.pk = pk
        self.not_null = not_null
        self.unique = unique
        self.default = default
class MockRef:
    def __init__(self, col, ref_table, ref_col, on_update, on_delete):
        self.col = col
        self.ref_table = ref_table
        self.ref_col = ref_col
        self.on_update = on_update
        self.on_delete = on_delete
class MockTable:
    def __init__(self, name, columns, refs):
        self.name = name
        self.columns = columns
        self.refs = refs
class MockIndex:
    def __init__(self, name, unique, subjects, table):
        self.name = name
        self.unique = unique
        self.subjects = subjects
        self.table = table

def SQLogger(inp):
    with open('./tests/output.sql', 'w') as s:
        s.write(inp)

def test_version():
    assert __version__ == '0.3.1'

def test_toSQLite():
    assert isinstance(toSQLite(), str)
    with pytest.raises(ValueError):
        toSQLite('./tests/asdf')
    with pytest.raises(ValueError):
        toSQLite('./tests/output.sql')
    o = toSQLite('./tests/sub')
    assert o.startswith('CREATE TABLE IF NOT EXISTS mytab ') 
    SQLogger(toSQLite('./tests/test.dbml'))

def test_validDBMLFile():
    assert validDBMLFile('asd.dbml')
    assert not validDBMLFile('asd')

def test_coercion():
    with pytest.raises(ValueError):
        coerceColType('asd')
    assert coerceColType('None') == 'NULL'
    assert coerceColType('integer') == 'INTEGER'
    assert coerceColType('tinyint') == 'INTEGER'
    assert coerceColType('float') == 'REAL'
    assert coerceColType('varchar') == 'TEXT'
    assert coerceColType('varchar(1)') == 'TEXT'
    assert coerceColType('varchar(0123)') == 'TEXT'
    with pytest.raises(ValueError):
        coerceColType('varchar(a)')
    assert coerceColType('byte') == 'BLOB'

def test_process_column():
    # name, Type, pk, not_null, unique, default
    c1 = MockColumn("c1", 1, None, None, None, None)
    c2 = MockColumn("c2", 'INTEGER', True, False, False, None)
    c3 = MockColumn("c3", 'REAL', False, True, True, None)
    c4 = MockColumn('c4', 'TEXT', False, False, False, 'howdy')
    i1 = MockItem('i1')
    i2 = MockItem('i2')
    e1 = MockEnum('e1', [i1, i2])
    c5 = MockColumn('c5', e1, False, True, False, None)
    with pytest.raises(TypeError):
        processColumn(c1, 'full')
    assert processColumn(c2, 'full') == '  c2 INTEGER PRIMARY KEY'
    assert processColumn(c3, 'full') == '  c3 REAL NOT NULL UNIQUE'
    assert processColumn(c4, 'full') == '  c4 TEXT DEFAULT \'howdy\''
    assert processColumn(c5, 'full') == '  c5 TEXT NOT NULL REFERENCES e1(type)'
    assert processColumn(c5, 'half') == '  c5 TEXT CHECK( c5 IN ( \'i1\', \'i2\' ) ) NOT NULL'

def test_process_ref():
    fc = MockColumn('foreign_key', None, None, None, None, None)
    t = MockTable('foreign_table', [fc], [])
    lc = MockColumn('local_key', None, None, None, None, None)
    r = MockRef(lc, t, fc, 'NO ACTION', 'NO ACTION')
    o = processRef(r)
    assert o == '  FOREIGN KEY(local_key) REFERENCES foreign_table(foreign_key) ON UPDATE NO ACTION ON DELETE NO ACTION'

def test_process_table():
    """
processTable(table, emulationMode, tableExists=True, join=True)
    1 ) multiple refs
    2 ) joined output
    """
    lc1 = MockColumn('l1', 'INTEGER', None, None, None, None)
    lc2 = MockColumn('l2', 'INTEGER', None, None, None, None)
    fc1 = MockColumn('f1', 'INTEGER', None, None, None, None)
    fc2 = MockColumn('f2', 'INTEGER', None, None, None, None)
    fortab = MockTable('ft', [fc1, fc2], [])
    r1 = MockRef(lc1, fortab, fc1, 'NO ACTION', 'NO ACTION')
    r2 = MockRef(lc2, fortab, fc2, 'NO ACTION', 'NO ACTION')
    loctab = MockTable('lt', [lc1, lc2], [r1, r2])
    o = processTable(loctab, 'full', False, True)
    assert o == "CREATE TABLE lt (\n  l1 INTEGER,\n  l2 INTEGER,\n  FOREIGN KEY(l1) REFERENCES ft(f1) ON UPDATE NO ACTION ON DELETE NO ACTION,\n  FOREIGN KEY(l2) REFERENCES ft(f2) ON UPDATE NO ACTION ON DELETE NO ACTION\n);\n"

def test_process_enum():
    items = []
    items.append(MockItem('Joe'))
    items.append(MockItem('Bob'))
    items.append(MockItem('Jimmy'))
    e = MockEnum('myEnum', items)
    o = processEnum(e)
    assert o == f'CREATE TABLE IF NOT EXISTS {e.name} (\n  id INTEGER PRIMARY KEY,\n  type TEXT NOT NULL UNIQUE,\n  seq INTEGER NOT NULL UNIQUE\n);\nINSERT INTO {e.name}(type, seq) VALUES (\'Joe\', 1);\nINSERT INTO {e.name}(type, seq) VALUES (\'Bob\', 2);\nINSERT INTO {e.name}(type, seq) VALUES (\'Jimmy\', 3);\n'

def test_process_file():
    p = Path('./tests/abc.dbml')
    o = processFile(p, 'full', True, True, MockNameFunc)
    assert o == 'CREATE TABLE IF NOT EXISTS mytab (\n  name TEXT,\n  phone INTEGER\n);\nCREATE INDEX IF NOT EXISTS _mockname ON mytab (name, phone);\n'

def test_process_index():
    mytab = MockTable('mytab', [], [])
    col1 = MockColumn('col1', None, None, None, None, None)
    col2 = MockColumn('col2', None, None, None, None, None)
    idx = MockIndex('myidx', False, [col1, col2], mytab)
    o = processIndex(mytab, idx, MockNameFunc, False, True)
    assert o == "CREATE INDEX myidx ON mytab (col1, col2);\n" 

def test_sqlite():
    if os.path.exists('./tests/example.db'):
        os.remove('./tests/example.db')
    con = sqlite3.connect('./tests/example.db')
    s = toSQLite('./tests/test.dbml')
    with con:
        con.executescript(s)
        q = """
            SELECT 
                name
            FROM 
                sqlite_master 
            WHERE 
                type ='table' AND 
                name NOT LIKE 'sqlite_%';
        """
        tables = con.cursor().execute(q)
        tables = [t[0] for t in tables]
        assert len(tables) == 4
        assert 'message' in tables
        assert 'message_status' in tables 
        assert 'contact' in tables
        assert 'zip_code' in tables 
    con.close()

    if os.path.exists('./tests/example2.db'):
        os.remove('./tests/example2.db')
    con = sqlite3.connect('./tests/example2.db')
    s = toSQLite('./tests/test.dbml', 'half')
    SQLogger(s)
    with con:
        con.executescript(s)
        q = """
            SELECT 
                name
            FROM 
                sqlite_master
            WHERE
                type ='table' AND
                name NOT LIKE 'sqlite_%';
        """
        tables = con.cursor().execute(q)
        tables = [t[0] for t in tables]
        assert len(tables) == 2
        assert 'message' in tables
        assert 'contact' in tables
    con.close() 
