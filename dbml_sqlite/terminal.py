import click
from .core import toSQLite
import sqlite3

@click.command()
@click.argument('src', type=click.Path(exists=True))
@click.option('--print/--no-print', '-p/-n', '_print', default=True, help='Whether to print output to console.', show_default=True)
@click.option('--write', '-w', type=click.Path(writable=True), help='(Optional) File you want output written to.')
@click.option('--execute', '-x', type=click.Path(writable=True), help='(Optional) SQLite database file for executing output DDL on. Will create file if it doesn\'t exist.')
@click.option('--full/--half', '-f/-h', default=True, help='Full emulation mode (separate tables) or half emulation mode (check statements) for any enums defined in your dbml.', show_default=True)
@click.option('--if-table-exists', '-t', 'table', is_flag=True, help='(Optional) Add IF NOT EXISTS language to CREATE TABLE statements.')
@click.option('--if-index-exists', '-i', 'index', is_flag=True, help='(Optional) Add IF NOT EXISTS language to CREATE INDEX statements.')
def cli(src, _print, write, execute, full, table, index):
    """Converts DBML contained in SRC file to SQLite DDL and does with that string of SQLite DDL what you want."""
    o = None
    try:
        mode = 'full' if full else 'half'
        o = toSQLite(src, mode, tableExists=table, indexExists=index)
    except:
        click.secho('Error generating SQLite DDL from dbml. Did you provide a valid dbml file?', fg="red", bold=True)
    else:
        if _print:
            click.echo(o)
        if write != None:
            with open(write, 'w') as f:
                f.write(o)
        if execute != None:
            con = sqlite3.connect(execute)
            with con:
                con.executescript(o)
            con.close()

