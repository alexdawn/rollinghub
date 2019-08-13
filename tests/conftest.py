import os
import pytest
from rollinghub import create_app
from rollinghub.db import get_db, init_db


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE': os.environ['DATABASE_URL'],
    })

    with app.app_context():
        init_db()
        get_db.executescript(_data_sql)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
