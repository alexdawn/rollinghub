from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from iso3166 import countries
import io

from rollinghub.auth import login_required
from rollinghub.db import get_db


bp = Blueprint('mod', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def index():
    db, cur = get_db()
    cur.execute(
        """
SELECT m.id, title, description, created, author_id, username
    FROM mod as m
    JOIN "user" as u
    ON m.author_id = u.id
    ORDER BY created DESC;
        """
    )
    posts = cur.fetchall()
    return render_template('mod/index.html', posts=posts)


@bp.route('/img/<int:mod_id>')
def image(mod_id):
    db, cur = get_db()
    cur.execute(
        """
SELECT thumbnail_name, thumbnail
    FROM mod as m
    WHERE id = %s
        """, (mod_id, )
    )
    mod = cur.fetchone()
    return send_file(
        io.BytesIO(mod['thumbnail']),
        mimetype='image/jpeg',
        attachment_filename=mod['thumbnail'])


@bp.route('/download/<int:mod_id>')
def download(mod_id):
    db, cur = get_db()
    cur.execute(
        """
SELECT filename, file
    FROM mod as m
    WHERE id = %s
        """, (mod_id, )
    )
    mod = cur.fetchone()
    return send_file(
        io.BytesIO(mod['file']),
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=mod['filename'])


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        vehicle = request.form['vehicle']
        country = ['foo'] #request.form['country']
        tags = list(request.form['tags'])
        body = request.form['body']
        request.files['files']
        error: str = None
        if not title:
            error = "Title is required"
        if 'files' not in request.files or 'thumbnail' not in request.files:
            flash("Missing File")
            return redirect(request.url)
        files = request.files['files']
        image = request.files['thumbnail']
        if files.filename == '' or image.filename == '':
            error = "No selected file"
        if error is not None:
            flash(error)
        if files and image and allowed_file(files.filename) and allowed_file(image.filename):
            filename = secure_filename(files.filename)
            imagename = secure_filename(image.filename)
            db, cur = get_db()
            cur.execute(
                """
INSERT INTO mod (title, description, author_id, mod_type, countries, tags,
                 filename, file, thumbnail_name, thumbnail)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, body, g.user['id'], vehicle, country, tags,
                      filename, files.read(), imagename, image.read())
            )
            db.commit()
            flash("Post succesful")
            return redirect(url_for('mod.index'))
        else:
            flash("Invalid File Type")
    return render_template('mod/create.html', countries=countries)


def get_post(id, check_author=True):
    db, cur = get_db()
    cur.execute(
        """
SELECT m.id, title, description, created, author_id, username
    FROM mod as m
    JOIN "user" as u
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
