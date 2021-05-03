import pytest
from dbml_sqlite import __version__
from dbml_sqlite import toSQLite, validDBMLFile

def test_version():
    assert __version__ == '0.1.0'

def test_toSQLite():
    assert isinstance(toSQLite(), str)
    with pytest.raises(ValueError):
        toSQLite('asdf')

def test_validDBMLFile():
    assert validDBMLFile('asd.dbml')
    assert not validDBMLFile('asd')
