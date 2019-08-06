from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from rollinghub.auth import login_required
from rollinghub.db import get_db

bp = Blueprint('mod', __name__)


@bp.route('/')
def index():
    db, cur = get_db()
    cur.execute(
        """
SELECT m.id, title, description, created, author_id, username
    FROM mod as m
    JOIN user as u
    ON m.author_id = u.id
        """
    )
    posts = cur.fetchall()
    return render_template('mod/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error: str = None
        if not title:
            error = "Title is required"
        if error is not None:
            flash(error)
        else:
            db, cur = get_db()
            cur.execute(
                """
INSERT INTO mod (title, description, author_id) VALUES (%s, %s, %s)
                """, (title, body, g.user['id'])
            )
            db.commit()
            flash("Post succesful")
            return redirect(url_for('mod.index'))
    return render_template('mod/create.html')


def get_post(id, check_author=True):
    db, cur = get_db()
    cur.execute(
        """
SELECT m.id, title, description, created, author_id, username
    FROM mod as m
    JOIN user as u
    ON m.author_id = u.id
    WHERE m.id = %s
        """, (id, )
    )
    post = cur.fetchone()
    if post is None:
        abort(404, "Post id {} does not exist".format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = 'Title is required'
        if error is not None:
            flash(error)
        else:
            db, cur = get_db()
            cur.execute(
                "UPDATE mod SET title = %s, description = %s WHERE id = %s",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('mod.index'))
    return render_template('mod/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
    get_post(id)
    db, cur = get_db()
    cur.execute('DELETE FROM mod WHERE id = %s', (id,))
    db.commit()
    return redirect(url_for('mod.index'))
