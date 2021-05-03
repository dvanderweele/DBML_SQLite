from dbml_sqlite import __version__
from dbml_sqlite import toSQLite, validDBMLFile

def test_version():
    assert __version__ == '0.1.0'

def test_toSQLite():
    assert isinstance(toSQLite(), str)

def test_validDBMLFile():
    assert validDBMLFile('asd.dbml')
    assert validDBMLFile('asd.DBML')
    assert validDBMLFile('ASD.DBML')
    assert not validDBMLFile('asd')
