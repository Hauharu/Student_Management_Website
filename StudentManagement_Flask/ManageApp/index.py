from tkinter.font import names

from wtforms.validators import email

from ManageApp import app, controller, login, dao
from flask import render_template, request, redirect, url_for, jsonify, session
from flask_login import login_user,logout_user, login_required  # Hỗ trợ xác thực người dùng
from ManageApp.models import *
# from  StudentManagement_Flask.ManageApp.decorators import logged_in
# import pdb


# Thiết lập khóa bí mật
app.secret_key = 'Admin@123'

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
       # print(f"username: {username}, role: {role}, user: {user}")

        user = dao.auth_user(username=username, password=password, role=role)

        if user:
            login_user(user=user)
            next = request.args.get('next')
            url = "/" + role.lower()
          #  print(f"Redirecting to: {next if next else url}")
            return redirect(next if next else url)
        else:
            err_msg = 'Tài khoản hoặc mật khẩu không đúng!'
    return render_template('login.html', err_msg=err_msg)

@app.route('/logout')
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))


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
        address=request.form.get("address")
        phoneNumber=request.form.get("phoneNumber")
        email=request.form.get("email")
        joined_date=request.form.get("joined_date")
        class_id=request.form.get("class_id")
    return render_template('tiepnhan.html')


@app.route('/dshocsinh')
@login_required
def dshocsinh():
    kw = request.args.get('kw')
    student = dao.get_student_list()
    return render_template('dshocsinh.html', student=student)

@app.route('/get_hoc_sinh/<int:id>', methods=['GET'])
def get_hoc_sinh(id):
    hs = Student.query.get(id)
    return jsonify({'id': hs.id,
                    'hoTen': hs.name,
                    'ngaySinh': hs.dateOfBirth,
                    'gioiTinh': hs.gender,
                    'diaChi': hs.address,
                    'soDT': hs. phoneNumber,
                    'email': hs.email,
                    'ngayNhapHoc': hs.joined_date,
                    'lop_id': hs.class_id})


@app.route('/get_class_list', methods=['GET'])
def get_danh_sach_lop():
    class_list = Class.query.all()
    return jsonify([{'id': lop.id, 'tenLop': lop.name, 'siSo': lop.siSo} for lop in class_list])


# Route để lấy thông tin lớp học
@app.route('/get_class/<int:id>', methods=['GET'])
def get_lop(id):
    lop = dao.get_class_by_id(id)
    return jsonify({'id': lop.id, 'tenLop': lop.name, 'siSo': lop.siSo})

@app.route('/dslop', methods=['GET', 'POST'])
def dslophoc():
    kw = request.args.get('kw')
    class_list=dao.get_class_list()
    return render_template('dslophoc.html', class_list=class_list)

# Hiển thị theo từng lớp
@app.route('/get_data', methods=['POST'])
def get_data():
    class_id = request.form.get('class_id')
    data = db.session.query(Class, Student).join(Student).filter(Class.id == class_id).all()

    # Format data as a list of dictionaries
    formatted_data = [
        {
            'id': student.id,
            'tenHocSinh': student.name,
            'gioiTinh': student.gender,
            'ngaySinh': student.dateOfBirth,
            'diaChi': student.address
        }
        for class_id , student in data
    ]

    return jsonify(formatted_data)


#Lấy học sinh theo lớp
@app.route('/classes/<int:class_id>/students')
def get_student_from_class(class_id):
    students = Student.query.filter_by(class_id=class_id).all()
    return jsonify({'students': [student.to_dict() for student in students]})


if __name__ == "__main__":
   # from StudentManagement_Flask.ManageApp.admin import *
    with app.app_context():
       app.run(debug=True)
