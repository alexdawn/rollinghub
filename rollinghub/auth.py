import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from rollinghub.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        password2 = request.form['password2']
        db, cur = get_db()
        error: str = None
        if not email:
            error = 'Email is required'
        elif not password:
            error = 'Password is required'
        elif not nickname:
            error = 'Nickname is required'
        elif password != password2:
            error = 'Passwords do not match'
        else:
            cur.execute(
                'SELECT id FROM "user" WHERE email = %s', (email, )
            )
            if cur.fetchone() is not None:
                error = 'Email {} is already taken'.format(email)

        if error is None:
            cur.execute(
                """
                INSERT INTO "user" (email, nickname, password)
                VALUES (%s, %s, %s)
                """,
                (email, nickname, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))
        else:
            flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db, cur = get_db()
        error: str = None
        cur.execute(
            'SELECT * FROM "user" where email = %s', (email,)
        )
        user = cur.fetchone()
        if user is None:
            error = 'Incorrect email'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            flash(error)
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db, cur = get_db()
        cur.execute(
            'SELECT * FROM "user" WHERE id = %s', (user_id, )
        )
        g.user = cur.fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("You must be logged in")
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view
