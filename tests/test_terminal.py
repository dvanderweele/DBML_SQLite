import pytest
import os
from dbml_sqlite import cli
from click.testing import CliRunner

def test_cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('src.dbml', 'w') as f:
            f.write('table tester {\n    id integer\n}')
        result = runner.invoke(cli, ['src.dbml', '-p'])
        assert result.output == "CREATE TABLE tester (\n  id INTEGER\n);\n\n"
        result = runner.invoke(cli, ['src.dbml', '--write', 'dst.ddl', '-t', '-x', 'my.db'])
        assert os.path.exists('my.db')
        with open('dst.ddl', 'r') as f:
            assert f.read() == 'CREATE TABLE IF NOT EXISTS tester (\n  id INTEGER\n);\n'
        with open('err.dbm1', 'w') as f:
            f.write('errrrrrr')
        result = runner.invoke(cli, ['err.dbm1'])
        assert 'Error generating SQLite DDL from dbml. Did you provide a valid dbml file?' in result.output
