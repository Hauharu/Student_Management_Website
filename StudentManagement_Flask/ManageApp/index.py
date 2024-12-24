import flash
from ManageApp import app, controller, login, dao
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_user,logout_user, login_required  # Hỗ trợ xác thực người dùng
from wtforms.validators import email
from ManageApp.models import *


app.secret_key="Admin@123"

# Định tuyến cho trang chủ
app.add_url_rule("/", 'index', controller.index)

# Định tuyến cho trang đăng nhập
app.add_url_rule("/user-login", 'user_signin',  controller.user_signin, methods=['GET', 'POST'])

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
    return  redirect(url_for('user_signin'))

#Chức năng Staff
@app.route('/staff')
@login_required
def staff():
    return render_template('staff/staff.html')

@app.route('/tiepnhan', methods=['GET', 'POST'])
def tiepnhan():
    err_msg=""
    if request.method.__eq__('POST'):
        name=request.form.get("name")
        gender=request.form.get("gender")
        dateOfBirth=request.form.get("dateOfBirth")
        address=request.form.get("address")
        phoneNumber=request.form.get("phoneNumber")
        email=request.form.get("email")
        admission_date=request.form.get("admission_date")
        class_id=request.form.get("class_id")
    return render_template('staff/tiepnhan.html')



@app.route('/dshocsinh')
@login_required
def dshocsinh():
    kw = request.args.get('kw')
    student = dao.get_student_list()
    return render_template('staff/dshocsinh.html', student=student)

@app.route('/dslop', methods=['GET', 'POST'])
def dslophoc():
    class_list=dao.get_class_list()
    return render_template('staff/dslophoc.html', class_list=class_list)

#Chức năng Teacher
@app.route('/teacher')
@login_required
def teacher():
    return render_template('teacher/teacher.html')

@app.route('/nhapdiem')
@login_required
def input_score():
    return render_template('teacher/nhapdiem.html')

@app.route('/dsmon')
@login_required
def dsmonhoc():
    subject = dao.get_subject_list()
    return render_template('teacher/dsmon.html', subject=subject)



if __name__ == "__main__":
    from ManageApp.admin import *
    app.run(debug=True)
