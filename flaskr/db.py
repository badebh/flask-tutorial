import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    # g is a special object which stores data that might be accessed
    # by multiple functions during a request
    if 'db' not in g:
        # connect to the database file
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
            )
        # return rows that look like dicts
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    '''
    Close the database connection if it was created.
    '''
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    '''
    Clear the existing data and create new tables.
    '''
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    '''
    Register close_db and init_db_command functions with a given
    app so they're available for use by said app.
    '''
    # call this function when cleaning up
    app.teardown_appcontext(close_db)
    # add a new command that can be called with flask
    app.cli.add_command(init_db_command)