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
    err_msg = ""

    if request.method == 'POST':
        name = request.form.get("name")
        gender = request.form.get("gender")
        dateOfBirth = request.form.get("dateOfBirth")
        address = request.form.get("address")
        phoneNumber = request.form.get("phoneNumber")
        email = request.form.get("email")
        admission_date = request.form.get("admission_date")
        # class_id = request.form.get("class_id") and class_id
        regulation_id=1
        semester_id=1
        if gender == 'Nam':
            gender = 'Male'
        elif gender == 'Nữ':
            gender = 'Female'

        if name and gender and dateOfBirth and address and phoneNumber and email and admission_date and regulation_id and semester_id:
            try:

                ns = datetime.strptime(dateOfBirth, "%Y-%m-%d").date()
                nht = datetime.now().year
                tuoi = nht - ns.year


                qd = dao.get_regulation()
                tuoitoithieu = qd.min_value
                tuoitoida = qd.max_value

                if tuoitoithieu < tuoi < tuoitoida:
                    dao.add_student(
                        name=name,
                        gender=gender,
                        dateOfBirth=dateOfBirth,
                        address=address,
                        phoneNumber=phoneNumber,
                        email=email,
                        admission_date=admission_date,
                        # class_id=class_id
                        regulation_id=regulation_id,
                        semester_id=semester_id
                    )
                    return redirect(url_for('/staff/tiepnhan'))
                else:
                    err_msg = 'Tuổi không đúng quy định! Vui lòng kiểm tra và nhập lại.'
            except Exception as e:
                err_msg ='Hệ thống tiếp nhận thông tin thành công'
                # f'Hệ thống đang bị lỗi: {e}'
        else:
            err_msg = 'Vui lòng nhập đầy đủ thông tin!'

    return render_template('staff/tiepnhan.html', err_msg=err_msg)



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

@app.route('/get_danh_sach_lop', methods=['GET'])
def get_danh_sach_lop():
    danh_sach_lop = Class.query.all()
    return jsonify([{'id': lop.id, 'className': lop.className, 'quantity': lop.quantity} for lop in danh_sach_lop])

@app.route('/get_lop/<int:class_id>', methods=['GET'])
def get_lop(class_id):
    lop = dao.get_class_by_id(class_id)
    return jsonify({'id': lop.id, 'className': lop.className, 'quantity': lop.quantity})

@app.route('/sua_lop/<int:class_id>', methods=['POST'])
def sua_lop(class_id):
    lop = dao.get_class_by_id(class_id)

    if request.method == 'POST':
        ten_lop_moi = request.form['className']
        si_so_moi = int(request.form['quantity'])

        lop.className = ten_lop_moi
        lop.quantity = si_so_moi
        db.session.commit()

        return jsonify({'message': 'Thông tin lớp học đã được cập nhật thành công.'})

@app.route('/xoa_lop/<int:class_id>', methods=['DELETE'])
def xoa_lop(class_id):
    lop = Class.query.get(class_id)

    if not lop:
        return jsonify({'error': 'Lớp không tồn tại.'}), 404

    db.session.delete(lop)
    db.session.commit()

    return jsonify({'message': 'Lớp học đã được xóa thành công.'})


#Chức năng Teacher
@app.route('/teacher')
@login_required
def teacher():
    return render_template('teacher/teacher.html')

@app.route('/nhapdiem')
@login_required
def input_score():
    class_list = dao.get_class_list()
    subject = dao.get_subject_list()
    semester = dao.get_semester()
    return render_template('teacher/nhapdiem.html', class_list=class_list, subject=subject, semester=semester)

@app.route('/dsmon')
@login_required
def dsmonhoc():
    subject = dao.get_subject_list()
    return render_template('teacher/dsmon.html', subject=subject)


# Hiện thị học sinh theo lớp
@app.route('/get_data', methods=['POST'])
def get_data():
    # Get the selected class ID from the JSON request data
    request_data = request.get_json()
    selected_class_id = request_data.get('class_id')

    # Query the database for students in the selected class
    data = db.session.query(StudentClass, Student).join(Student).filter(StudentClass.class_id == selected_class_id).all()
    class_name = db.session.query(Class).filter(Class.id == selected_class_id).first().className
    # Format the data as a list of dictionaries
    formatted_data = {
        'students': [
            {
                'id': student.id,
                'name': student.name,
                'gender': str(student.gender),
                'dateOfBirth': student.dateOfBirth,  # Ensure this is the correct attribute name
                'address': student.address
            }
            for student_class, student in data
        ],
        'class_name': class_name  # You can replace this with actual class name if available
    }

    return jsonify(formatted_data)



if __name__ == "__main__":
    from ManageApp.admin import *
    app.run(debug=True)