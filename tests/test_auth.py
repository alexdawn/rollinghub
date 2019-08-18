import pytest
from flask import g, session
from rollinghub.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={
            'email': 'a@b.com', 'nickname': 'a', 'password': 'a', 'password2': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        db, cur = get_db()
        cur.execute(
            "Select * from \"user\" where email = 'a@b.com'"
        )
        assert cur.fetchone() is not None


@pytest.mark.parametrize(('email', 'nickname', 'password', 'password2', 'message'), (
    ('', '', '', '', b'Email is required'),
    ('a@b.com', '', '', '', b'Nickname is required'),
    ('a@b.com', 'a', '', '', b'Password is required'),
    ('test@test.com', 'testman', 'test', 'test', b'Email test@test.com is already taken'),
    ('new@test.com', 'testman', 'test', 'test', b'Nickname testman is already taken'),
    ('a@b.com', 'a', 'password', 'notpassword', b'Passwords do not match'),
))
def test_register_validate_input(client, email, nickname, password, password2, message):
    response = client.post(
        '/auth/register',
        data={
            'email': email, 'nickname': nickname,
            'password': password, 'password2': password2}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['id'] == 1
        assert g.user['nickname'] == 'testman'


@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('a', 'foo', b'Incorrect email or password'),
    ('test@test.com', 'a', b'Incorrect email or password'),
))
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
