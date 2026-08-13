from functools import wraps

from flask import abort, redirect, request, url_for
from flask_login import current_user

from flaskblog import bcrypt


def redirect_authenticated_user(view):
    """Redirect already-authenticated users to the home page.

    Applied to views (register, login, password reset) that should only be
    reachable by anonymous visitors.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return view(*args, **kwargs)
    return wrapped


def hash_password(password):
    """Return a bcrypt hash of the given plaintext password."""
    return bcrypt.generate_password_hash(password).decode('utf-8')


def abort_if_not_author(post):
    """Abort with 403 unless the current user authored the given post."""
    if post.author != current_user:
        abort(403)


def get_page():
    """Return the requested pagination page from the query string (default 1)."""
    return request.args.get('page', 1, type=int)
