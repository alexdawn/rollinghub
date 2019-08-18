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
        db, cur = get_db()
        cur.execute(_data_sql)
        db.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@test.com', password='test'):
        return self._client.post(
            '/auth/login',
            data={
                'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
