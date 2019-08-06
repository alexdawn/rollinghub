import urllib.parse as urlparse
import click
from flask import current_app, g
from flask.cli import with_appcontext
import psycopg2


def get_db():
    if 'db' not in g:
        url = urlparse.urlparse(current_app.config['DATABASE'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        g.db = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )
    return g.db, g.db.cursor()


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db, cur = get_db()
    with current_app.open_resource('schema.sql') as f:
        cur.execute(f.read().decode('utf8'))
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")

if __name__ == "__main__":
    init_db()
