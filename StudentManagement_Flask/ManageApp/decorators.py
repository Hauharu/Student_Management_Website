from functools import wraps
from flask import request, redirect, url_for
from flask_login import current_user
from ManageApp.models import UserRole

def annonynous_user(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect('/')

        return f(*args, **kwargs)

    return decorated_func


def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            next = request.url
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def teacher_requirement(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):

        if current_user.user_role == UserRole.TEACHER or current_user.user_role == UserRole.ADMIN:
            return f(*args, **kwargs)

        else:
            return redirect(url_for('access_denied'))

    return decorated_func


def staff_requirement(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):

        if current_user.user_role == UserRole.STAFF or current_user.user_role == UserRole.ADMIN:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('access_denied'))

    return decorated_func


def admin_requirement(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_role == UserRole.ADMIN:
            return redirect('/admin')

        return f(*args, **kwargs)

    return decorated_func
