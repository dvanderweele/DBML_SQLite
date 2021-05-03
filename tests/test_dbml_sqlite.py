import pytest
from dbml_sqlite import __version__
from dbml_sqlite import toSQLite, validDBMLFile, coerceColType

def test_version():
    assert __version__ == '0.1.0'

def test_toSQLite():
    assert isinstance(toSQLite(), str)
    with pytest.raises(ValueError):
        toSQLite('asdf')

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

