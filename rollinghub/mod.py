from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from rollinghub.auth import login_required
from rollinghub.db import get_db

bp = Blueprint('mod', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        """
SELECT m.id, title, description, created, author_id, username
    FROM mod as m
    JOIN user as u
    ON m.author_id = u.id
        """
    ).fetchall()
    return render_template('mod/index.html', posts=posts)
