from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from iso3166 import countries as countries_list
import io


from rollinghub.auth import login_required
from rollinghub.db import get_db
from rollinghub.zipper import make_zip, extract_zip


bp = Blueprint('model', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def index():
    db, cur = get_db()
    cur.execute(
        """
SELECT m.id, title, description, m.created, author_id, nickname
    FROM model as m
    JOIN "user" as u
    ON m.author_id = u.id
    ORDER BY created DESC;
        """
    )
    posts = cur.fetchall()
    return render_template('model/index.html', posts=posts)


@bp.route('/img/<int:model_id>')
def image(model_id):
    db, cur = get_db()
    cur.execute(
        """
SELECT thumbnail_name, thumbnail
    FROM model as m
    WHERE id = %s
        """, (model_id, )
    )
    model = cur.fetchone()
    return send_file(
        io.BytesIO(model['thumbnail']),
        mimetype='image/jpeg',
        attachment_filename=model['thumbnail_name'])


@bp.route('/download/<int:model_id>')
def download(model_id):
    db, cur = get_db()
    cur.execute(
        """
SELECT m.title as model_name, v.name as variant_name, l.name as livery_name,
       body.obj_file as body,
       bogie_front.obj_file as bogie_front,
       bogie_back.obj_file as bogie_back,
       coupler_front.obj_file  as coupler_front,
       coupler_back.obj_file  as coupler_back,
       config_file,
       texture_file
    FROM model as m
    JOIN variant as v
        ON m.id = v.model_ref
    JOIN liveries as l
        on v.id = l.variant_ref
    JOIN object_files as body
        on v.body_ref = body.id
    JOIN object_files as bogie_front
        on v.bogie_front_ref = bogie_front.id
    JOIN object_files as bogie_back
        on v.bogie_back_ref = bogie_back.id
    JOIN object_files as coupler_front
        on v.coupler_front_ref = coupler_front.id
    JOIN object_files as coupler_back
        on v.coupler_back_ref = coupler_back.id
    WHERE m.id = %s
        """, (model_id, )
    )
    model = cur.fetchone()
    files = [
        ('quickMod_model_body.obj', model['body']),
        ('quickMod_model_wheels_front.obj', model['bogie_front']),
        ('quickMod_model_wheels_back.obj', model['bogie_back']),
        ('quickMod_model_couple_front.obj', model['coupler_front']),
        ('quickMod_model_couple_back.obj', model['coupler_back']),
        ('mod.txt', model['config_file']),
        ('quickMod_texture.png', model['texture_file'])
    ]
    folder_name = '{}-{}-{}'.format(
        model['model_name'], model['variant_name'], model['livery_name'])
    built_zip = make_zip(folder_name, files)
    return send_file(
        built_zip,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='{}.zip'.format(folder_name))


def add_model_to_db(db, cur, dict_values):
    cur.execute("""
WITH model_result AS (
INSERT INTO model (
    title, description, author_id, model_type, countries, manufacturer_ref, tags,
    thumbnail_name, thumbnail)
VALUES (%(model_title)s,
        %(model_description)s,
        %(author_id)s,
        %(model_type)s,
        %(countries)s,
        %(manufacturer_ref)s,
        %(model_tags)s,
        %(thumbnail_name)s,
        %(thumbnail)s)
RETURNING id
),
body AS (
INSERT INTO object_files (obj_file, object_type)
VALUES (%(body)s, 'body')
RETURNING id, object_type
),
bogies_front AS (
INSERT INTO object_files (obj_file, object_type)
VALUES (%(bogies_front)s, 'bogies')
RETURNING id, object_type
),
bogies_back AS (
INSERT INTO object_files (obj_file, object_type)
VALUES (%(bogies_back)s, 'bogies')
RETURNING id, object_type
),
couplers_front AS (
INSERT INTO object_files (obj_file, object_type)
VALUES (%(couplers_front)s, 'coupler')
RETURNING id, object_type
),
couplers_back AS (
INSERT INTO object_files (obj_file, object_type)
VALUES (%(couplers_back)s, 'coupler')
RETURNING id, object_type
),
variant_result AS (
INSERT INTO variant (
    author_id, model_ref, name, description, tags,
    body_ref, bogie_front_ref, bogie_back_ref, coupler_front_ref, coupler_back_ref,
    config_file)
    SELECT
    %(author_id)s, model_result.id, %(variant_name)s, %(variant_description)s,
    %(variant_tags)s, body.id, bogies_front.id, bogies_back.id, couplers_front.id, couplers_back.id,
    %(config_file)s
    FROM model_result, body, bogies_front, bogies_back, couplers_front, couplers_back
RETURNING id
)
INSERT INTO liveries (
    author_id, variant_ref, name, description, operator_ref, texture_file)
    SELECT
    %(author_id)s, variant_result.id, %(livery_name)s, %(livery_description)s,
    %(operator_ref)s, %(texture_file)s
    FROM variant_result;
            """, dict_values)
    db.commit()


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        model_title = request.form['model_title']
        model_type = request.form['model_type']
        countries = request.form.get('countries')
        manufacturer_ref = request.form.get('manufacturer_ref')
        model_tags = list(request.form.get('model_tags', ''))
        model_description = request.form['model_description']
        variant_name = request.form['variant_name']
        variant_description = request.form['variant_name']
        variant_tags = list(request.form['variant_tags'])
        livery_name = request.form['livery_name']
        livery_description = request.form['livery_description']
        operator_ref = request.form.get('operator_ref')
        request.files['files']
        error: str = None
        if not model_title:
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
            imagename = secure_filename(image.filename)
            zip_files = extract_zip(files)
            db, cur = get_db()
            add_model_to_db(db, cur, {
                "model_title": model_title,
                "model_description": model_description,
                "author_id": g.user['id'],
                "model_type": model_type,
                "countries": countries,
                "manufacturer_ref": manufacturer_ref,
                "model_tags": model_tags,
                "thumbnail_name": imagename,
                "thumbnail": image.read(),
                "body": zip_files['quickMod_model_body.obj'],
                "bogies_front": zip_files['quickMod_model_wheels_front.obj'],
                "bogies_back": zip_files['quickMod_model_wheels_back.obj'],
                "couplers_front": zip_files['quickMod_model_couple_front.obj'],
                "couplers_back": zip_files['quickMod_model_couple_back.obj'],
                "variant_name": variant_name,
                "variant_description": variant_description,
                "variant_tags": variant_tags,
                "config_file": zip_files['mod.txt'],
                "livery_name": livery_name,
                "livery_description": livery_description,
                "operator_ref": operator_ref,
                "texture_file": zip_files['quickMod_texture.png']
            })
            flash("Post succesful")
            return redirect(url_for('model.index'))
        else:
            flash("Invalid File Type")
    return render_template('model/create.html', countries_list=countries_list)


def get_post(id, check_author=True):
    db, cur = get_db()
    cur.execute(
        """
SELECT m.id, title, description, m.created, author_id, nickname
    FROM model as m
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
                "UPDATE model SET title = %s, description = %s WHERE id = %s",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('model.index'))
    return render_template('model/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
    get_post(id)
    db, cur = get_db()
    cur.execute('DELETE FROM model WHERE id = %s', (id,))
    db.commit()
    return redirect(url_for('model.index'))
