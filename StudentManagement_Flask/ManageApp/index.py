from ManageApp import app, controller, login, dao
from flask import render_template, request, redirect, url_for
from flask_login import login_user,logout_user, login_required  # Hỗ trợ xác thực người dùng
from ManageApp.models import *

# Định tuyến cho trang chủ
app.add_url_rule("/", 'index', controller.index)

# Định tuyến cho trang đăng nhập
app.add_url_rule("/user-login", 'user_signin', controller.user_signin, methods=['GET', 'POST'])

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


@app.route("/login", methods=['get', 'post'])
def user_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = dao.auth_user(username=username, password=password, role=role)
        if user:
            login_user(user)

            next = request.args.get('next')
            url = "/" + role.lower()
            return redirect(next if next else url)
        else:
            err_msg = 'Tài khoản hoặc mật khẩu không đúng!'

    return render_template('login.html', err_msg=err_msg)

@app.route('/logout')
def user_logout():
    logout_user()
    return  redirect(url_for(user_login))

if __name__ == "__main__":
    from ManageApp.admin import *
    app.run(debug=True)