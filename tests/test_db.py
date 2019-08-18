import psycopg2

import pytest
from rollinghub.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db, cur = get_db()
        db2, cur2 = get_db()
        assert db == db2

    with pytest.raises(psycopg2.InterfaceError) as e:
        cur.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('rollinghub.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called
