from flask import render_template
from flask_login import login_required

from . import main
from ..decorators import guest_required


@main.app_errorhandler(401)
@guest_required
def permission_denied(e):
    # return render_template('errors/error_403.html'), 403
    return '<h1>Log in Please</h1>', 401


@main.app_errorhandler(404)
def page_not_found(e):
    # return render_template('errors/error_404.html'), 404
    return '<h1>Page not found</h1>', 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/error_500.html'), 500
