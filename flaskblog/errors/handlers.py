import traceback
from flask import Blueprint, render_template, current_app
from flaskblog import db

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(500)
def error_500(error):
    # Roll back any half-finished transaction so a failed request does not
    # leave the session in a broken state for subsequent requests.
    db.session.rollback()
    current_app.logger.exception('Unhandled server error', exc_info=error)
    # Temporarily show full traceback for debugging on Render
    tb = traceback.format_exc()
    return f"<pre style='background:#111;color:#f88;padding:20px;font-size:13px;'><b>500 Error — Debug Info</b>\n\n{tb}</pre>", 500
