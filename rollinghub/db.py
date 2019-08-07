import click
from flask import current_app, g
from flask.cli import with_appcontext
import psycopg2
import psycopg2.extras


def get_db():
    if 'db' not in g:
        url = current_app.config['DATABASE']
        sslmode = 'require' if current_app.config['SSL_REQUIRE'] else 'allow'
        g.db = psycopg2.connect(url, sslmode=sslmode)
    return g.db, g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db, cur = get_db()
    with current_app.open_resource('schema.sql') as f:
        cur.execute(f.read())
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
