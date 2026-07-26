import logging

from flask import Blueprint, render_template, current_app

errors = Blueprint('errors', __name__)

logger = logging.getLogger(__name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(500)
def error_500(error):
    # Log the full traceback server-side (visible in Render logs) — never expose to users
    current_app.logger.exception("Unhandled 500 error: %s", error)
    return render_template('errors/500.html'), 500

