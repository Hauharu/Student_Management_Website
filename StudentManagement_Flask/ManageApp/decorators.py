from functools import wraps
from flask import request, redirect, url_for
from flask_login import current_user
from ManageApp.models import UserRole

# Người dùng chưa đăng nhập là ai
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


# Yêu cầu mật khẩu khi đăng nhập trang admin
def admin_requirement(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_role == UserRole.ADMIN:
            return redirect('/admin')

        return f(*args, **kwargs)

    return decorated_func
