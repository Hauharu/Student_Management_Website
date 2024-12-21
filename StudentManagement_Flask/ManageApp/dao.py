import hashlib
from ManageApp.models import *  # Import model User
from ManageApp import app, db    # SQLAlchemy session


def get_user_by_username(username):
    return User.query.filter(User.username == username).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()

def auth_user(username, password, role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(role)).first()
#
# def get_all_student_info():
#     active_students = Student.query.filter_by(is_active=True).all()
#     student_info = []
#     for student in active_students:
#         info = {
#             'id': student.id,
#             'name': student.name,
#             'gender': student.gender.name,
#             'joined_date': student.joined_date.strftime('%d-%m-%Y') if student.joined_date else '',
#             # 'dob': student.dob.strftime('%d-%m-%Y') if student.dob else ''
#         }
#         student_info.append(info)
#     return student_info
#
#
#
#
# def create_or_update_student(id=None, **kwargs):
#     # Cập nhật thông tin học sinh có sẵn
#     if id:
#         student = Student.query.get(id)
#         if student:
#             for key, value in kwargs.items():
#                 setattr(student, key, value)
#     # Tạo mới học sinh
#     else:
#         student = Student(**kwargs)
#         db.session.add(student)
#
def get_student_by_id(id):
    return Student.query.get(id)

def get_student_list(kw=None):
    student = Student.query

    if kw:
        student = Student.filter(Student.name.contains(kw))

    return student.all()

def get_add_student(name, dateOfBirth, address, phoneNumber, email, joined_date, class_id):
    st=Student(name=name, dateOfBirth=dateOfBirth, address=address,phoneNumber=phoneNumber,email=email,joined_date=joined_date,class_id=class_id)

    db.session.add(st)
    db.session.commit()

def get_class_by_id(id):
    return Class.query.get(id)

def get_class_list(kw=None):
    class_list = Class.query

    if kw:
        class_list = Class.filter(Class.name.contains(kw))

    return class_list.all()