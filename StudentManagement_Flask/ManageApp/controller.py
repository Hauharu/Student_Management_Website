import math
import hashlib
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from ManageApp import app, admin, dao, models, login
from ManageApp.decorators import *


def index():
    return render_template('index.html')


def access_denied():
    return render_template('layout/page_denied.html')

@app.route('/signout', methods=['GET', 'POST'])
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/signin', methods=['GET', 'POST'])
@annonynous_user
def user_signin():
    err_msg = ''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        user = dao.auth_user(username=username, password=password)
        if user and user.password == password:
            login_user(user=user)
            return redirect(url_for('index'))

        flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')

    return render_template('login.html', err_msg=err_msg)

@admin_requirement
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.check_login(username=username, password=password, role=models.UserRole.ADMIN)

    if user:
        login_user(user=user)

    return redirect('/admin')

