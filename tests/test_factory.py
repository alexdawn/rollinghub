from rollinghub import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    response = client.get('/')
    assert bytes('rollinghub', 'utf-8') in response.data
