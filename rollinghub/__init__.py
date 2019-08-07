import os
from flask import Flask
from . import db, auth, mod


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ['SECRET'] if os.environ.get('IS_HEROKU') else 'dev',
        DATABASE=os.environ['DATABASE_URL'],
        SSL_REQUIRE=True if os.environ.get('IS_HEROKU') else False
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(mod.bp)
    app.add_url_rule('/', endpoint='index')
    return app
