import pytest
from dbml_sqlite import __version__
from dbml_sqlite import toSQLite, validDBMLFile, coerceColType, processColumn, processRef, processEnum, processTable
from pydbml.classes import Enum

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

def SQLogger(inp):
    with open('./tests/output.sql', 'w') as s:
        s.write(inp)

def test_version():
    assert __version__ == '0.1.0'

def test_toSQLite():
    assert isinstance(toSQLite(), str)
    with pytest.raises(ValueError):
        toSQLite('asdf')
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
    pass

def test_process_ref():
    fc = MockColumn('foreign_key', None, None, None, None, None)
    t = MockTable('foreign_table', [fc], [])
    lc = MockColumn('local_key', None, None, None, None, None)
    r = MockRef(lc, t, fc, 'NO ACTION', 'NO ACTION')
    o = processRef(r)
    assert o == '  FOREIGN KEY(local_key) REFERENCES foreign_table(foreign_key) ON UPDATE NO ACTION ON DELETE NO ACTION'

def test_process_enum():
    items = []
    items.append(MockItem('Joe'))
    items.append(MockItem('Bob'))
    items.append(MockItem('Jimmy'))
    e = MockEnum('myEnum', items)
    o = processEnum(e)
    assert o == f'CREATE TABLE {e.name} IF NOT EXISTS (\n  id INTEGER PRIMARY KEY,\n  type TEXT NOT NULL UNIQUE,\n  seq INTEGER NOT NULL UNIQUE\n);\nINSERT INTO {e.name}(type, seq) VALUES (\'Joe\', 1);\nINSERT INTO {e.name}(type, seq) VALUES (\'Bob\', 2);\nINSERT INTO {e.name}(type, seq) VALUES (\'Jimmy\', 3);'

def test_process_table():
    pass

# TEST_TODO                                                                # processColumn
# processTable
