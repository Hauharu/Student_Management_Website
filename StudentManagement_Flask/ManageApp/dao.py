import hashlib
import smtplib
from flask import render_template_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ManageApp.models import *
from sqlalchemy import desc, func, select, case, distinct
from ManageApp import app, db  # SQLAlchemy session


# lấy tên đăng nhập người dùng
def get_user_by_username(username):
    return User.query.filter(User.username == username).first()


# lấy id người dùng
def get_user_by_id(user_id):
    return User.query.get(user_id)


# xác thực người dùng
def auth_user(username, password, role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(role)).first()


# lấy mật khẩu người dùng
def get_password_by_user_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.password


# đổi mật khẩu
def change_password(user_id, password):
    user = User.query.filter_by(id=user_id).first()
    user.password = password
    db.session.commit()


# băm mật khẩu
def hash_password(passw):
    password = str(hashlib.md5(passw.strip().encode('utf8')).hexdigest())
    return password


# check đăng nhập vai trò gì
def check_login(username, password, role):
    if username and password:
        password = hash_password(password)

        return User.query.filter((User.username.__eq__(username.strip())),
                                 User.password.__eq__(password.strip()),
                                 User.user_role.__eq__(role)).first()


# thêm người dùng
def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()


# học sinh
def user_count():
    with app.app_context():
        user_roles_count = db.session.query(User.user_role, func.count(User.id)) \
            .group_by(User.user_role).all()
        student_count = db.session.query(func.count(Student.id)).scalar()
        result = [(UserRole(role).value, count) for role, count in user_roles_count]
        result.append(("HỌC SINH", student_count))

        return result


# lấy học kỳ
def get_period(semester, year):
    return db.session.query(Semester).filter_by(semester=semester, year=year).first()


# thống kê số lượng học sinh theo học kỳ
def stats_amount_of_students_by_period(semester=SemesterType.SEMESTER_1.name, year=datetime.now().year.__str__()):
    period = get_period(semester, year)
    if period:
        query = (db.session.query(Class.className, func.count(StudentClass.student_id))
                 .join(StudentClass)
                 .filter(StudentClass.semester_id == period.id)
                 .group_by(Class.className)
                 )
        return query.all()
    else:
        return []


# lấy học sinh bằng id
def get_student_by_id(id):
    return Student.query.get(id)


# lấy danh sách học sinh
def get_student_list():
    student = Student.query.all()
    return student


# thêm học sinh
def add_student(name, gender, dateOfBirth, address, phoneNumber, email, admission_date, regulation_id, semester_id):
    new_student = Student(
        name=name,
        gender=gender,
        dateOfBirth=dateOfBirth,
        address=address,
        phoneNumber=phoneNumber,
        email=email,
        admission_date=admission_date,
        # class_id=class_id , class_id
        regulation_id=regulation_id,
        semester_id=semester_id
    )
    db.session.add(new_student)
    db.session.commit()
    return new_student.id


# them hoc sinh vao lop
def add_student_class(student_id, class_id, semester_id):
    new_student_class = StudentClass(
        student_id=student_id,
        class_id=class_id,
        semester_id=semester_id
    )
    db.session.add(new_student_class)
    db.session.commit()
    return new_student_class.id


# lay lop bang id
def get_class_by_id(id):
    return Class.query.get(id)


# lay danh sach lop
def get_class_list():
    class_list = Class.query.all()
    return class_list


# lay danh sach mon hoc
def get_subject_list():
    subject = Subject.query.all()
    return subject


# lay quy dinh
def get_regulation():
    qd = Regulation.query
    return qd.first()


# lay hoc ky
def get_semester():
    s = Semester.query
    return s.all()


# Chức năng cho Admin
def get_current_year():
    if datetime.now().month < 6:
        return datetime.now().year - 1
    return datetime.now().year


# lay hoc ky
def get_period(semester, year):
    return db.session.query(Semester).filter_by(semester=semester, year=year).first()


# thong ke so hoc sinh theo hoc ky
def stats_students_count_by_period(semester=SemesterType.SEMESTER_1.name, year=datetime.now().year.__str__()):
    period = get_period(semester, year)
    if period:
        query = (db.session.query(Class.className, func.count(StudentClass.student_id))
                 .join(StudentClass)
                 .filter(StudentClass.semester_id == period.id)
                 .group_by(Class.className)
                 )
        return query.all()
    else:
        return []


# khoi tao quy dinh
def init_regulation():
    existing_policies = Regulation.query.all()
    if existing_policies:
        return

    # Create default policies
    default_policies = [
        {"content": "Số tuổi tối thiểu nhập học", "data": 15},
        {"content": "Số tuổi tối đa nhập học", "data": 20},
        {"content": "Sĩ số tối đa của 1 lớp", "data": 40},
    ]

    # Insert default policies into the database
    for regulation_data in default_policies:
        regulation = Regulation(**regulation_data)
        db.session.add(regulation)

    # Commit changes to the database
    db.session.commit()


# lay mon hoc
def get_subjects():
    return db.session.query(Subject).all()


# lay nam
def get_years():
    query = db.session.query(Semester.year).all()
    years = {year[0] for year in query}
    return years


# lay so hoc sinh mot lop bng mon hoc va hoc ky
def count_students_of_classes_by_subject_and_period(subject_id, semester, year, avg_gt_or_equal_to=None):
    period = get_period(semester=semester, year=year)
    if not period:
        return []

    weighted_scores_subquery = (
        db.session.query(
            Student.id.label('student_id'),
            func.sum(
                case(
                    (ScoreDetail.type == 'EXAM_15MINS', ScoreDetail.score * 1),
                    (ScoreDetail.type == 'EXAM_45MINS', ScoreDetail.score * 2),
                    (ScoreDetail.type == 'EXAM_FINAL', ScoreDetail.score * 2),
                    else_=0
                )
            ).label('total_weighted_score'),
            func.sum(
                case(
                    (ScoreDetail.type == 'EXAM_15MINS', 1),
                    (ScoreDetail.type == 'EXAM_45MINS', 2),
                    (ScoreDetail.type == 'EXAM_FINAL', 2),
                    else_=0
                )
            ).label('total_weight')
        )
        .join(Score, Student.id == Score.student_id)
        .join(ScoreDetail, Score.scoreDetail_id == ScoreDetail.id)
        .filter(Score.subject_id == subject_id, Score.semester_id == period.id)
        .group_by(Student.id)
    ).subquery()

    weighted_avg_score = ((weighted_scores_subquery.c.total_weighted_score / weighted_scores_subquery.c.total_weight)
                          .label('avg_weighted_score')
                          )

    # Base query to retrieve classes and count of students
    base_query = (
        db.session.query(Class.id, Class.className, func.count(distinct(Student.id)))
        .join(Teach)
        .join(StudentClass, Class.id == StudentClass.class_id, isouter=True)
        .join(Student, isouter=True)
        .filter(StudentClass.semester_id == period.id)
        .group_by(Class.id)
    )

    # If average score condition is provided, add it to the query
    if avg_gt_or_equal_to is not None:
        base_query = (
            base_query
            .join(weighted_scores_subquery, Student.id == weighted_scores_subquery.c.student_id)
            .filter(weighted_avg_score >= avg_gt_or_equal_to)
        )

    return base_query.all()


# lay mon hoc bang id
def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)


# lay lop theo ten
def get_class_by_name(class_name):
    return db.session.query(Class).filter(Class.className == class_name).first()


# lay mot hoc sinh la duy nhat
def get_student_by_unique_fields(name, phoneNumber, email):
    return db.session.query(Student).filter(
        Student.name == name,
        Student.phoneNumber == phoneNumber,
        Student.email == email
    ).first()


# lay hoc sinh bang ten,so dien thoai,email khong bi trung
def get_student_by_name_phone_email(name, phoneNumber, email):
    return Student.query.filter(
        (Student.name == name) |
        (Student.phoneNumber == phoneNumber) |
        (Student.email == email)
    ).first()


# kiem tra trung lap
def check_duplicate(name, phoneNumber, email):
    # Kiểm tra trùng lặp học sinh theo tên, số điện thoại và email
    student = db.session.query(Student).filter(
        (Student.name == name) |
        (Student.phoneNumber == phoneNumber) |
        (Student.email == email)
    ).first()

    # Nếu có học sinh trùng thì trả về True, nếu không thì trả về False
    if student:
        return True
    return False


def send_email(to_email, student_name):
    sender_email = "trunghauu71@gmail.com"
    sender_password = "yourpassword"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Tạo nội dung email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "Thông báo tiếp nhận học sinh"

        body = f"""
        Xin chào {student_name},

        Trường trung học phổ thông OPEN đã tiếp nhận hồ sơ của bạn. Chào mừng bạn đến với trường học của chúng tôi!

        Thông tin chi tiết sẽ được gửi qua các kênh liên lạc khác.

        Trân trọng,
        Phòng tiếp nhận học sinh
        """
        msg.attach(MIMEText(body, 'plain'))

        # Kết nối đến máy chủ SMTP và gửi email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print("Email đã được gửi thành công!")
    except Exception as e:
        print(f"Lỗi khi gửi email: {str(e)}")
