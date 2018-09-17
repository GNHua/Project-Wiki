from functools import wraps
from flask import flash, url_for, redirect, request, abort
from flask_login import current_user
from mongoengine.connection import MongoEngineConnectionError
from .models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(group, *args, **kwargs):
            try:
                if not current_user.can(group, permission):
                    flash("Log in to access this page.")
                    return redirect(url_for('auth.wiki_group_login', 
                                            group=group, 
                                            next=request.url))
                return f(group, *args, **kwargs)
            except MongoEngineConnectionError:
                abort(404)

        return decorated_function

    return decorator


def super_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_super_admin():
            flash('Must log in as super admin.')
            return redirect(url_for('auth.wiki_super_login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def user_required(f):
    return permission_required(Permission.WRITE)(f)


def guest_required(f):
    return permission_required(Permission.READ)(f)
