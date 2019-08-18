import psycopg2
import psycopg2.extras
import os


def get_db():
    url = os.environ['DATABASE_URL']
    sslmode = 'require'
    db = psycopg2.connect(url, sslmode=sslmode)
    return db, db.cursor(cursor_factory=psycopg2.extras.DictCursor)


def init_db():
    db, cur = get_db()
    with open('./schema.sql', 'r') as f:
        cur.execute(f.read())
    db.commit()


init_db()
