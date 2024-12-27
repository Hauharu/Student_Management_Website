import hashlib
from ManageApp.models import *
from sqlalchemy import desc, func, select, case
from ManageApp import app, db  # SQLAlchemy session


def get_user_by_username(username):
    return User.query.filter(User.username == username).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)



def auth_user(username, password, role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(role)).first()

def hash_password(passw):
    password = str(hashlib.md5(passw.strip().encode('utf8')).hexdigest())
    return password


def check_login(username, password, role):
    if username and password:
        password = hash_password(password)

        return User.query.filter((User.username.__eq__(username.strip())),
                                 User.password.__eq__(password.strip()),
                                 User.user_role.__eq__(role)).first()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()



def user_count():
    with app.app_context():
        result = db.session.query(User.user_role, func.count(User.id)) \
            .group_by(User.user_role).all()
        return [(UserRole(role).value, count) for role, count in result]

#
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


def get_student_list():
    student = Student.query.all()
    return student


def add_student(name, gender, dateOfBirth, address, phoneNumber, email, admission_date, class_id):
    new_student = Student(
        name=name,
        gender=gender,
        dateOfBirth=dateOfBirth,
        address=address,
        phoneNumber=phoneNumber,
        email=email,
        admission_date=admission_date,
        class_id=class_id
    )
    db.session.add(new_student)
    db.session.commit()
    return new_student


def get_class_by_id(id):
    return Class.query.get(id)


def get_class_list():
    class_list = Class.query.all()
    return class_list


def get_subject_list():
    subject = Subject.query.all()
    return subject


# Chức năng cho Admin
def get_period(semester, year):
    return db.session.query(Semester).filter_by(semester=semester, year=year).first()

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

def get_subjects():
    return db.session.query(Subject).all()


def get_years():
    query = db.session.query(Semester.year).all()
    years = {year[0] for year in query}
    return years


def count_students_of_classes_by_subject_and_period(subject_id, semester_id, year, avg_gt_or_equal_to=None):
    period = get_period(semester=semester_id, year=year)
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
        .filter(Score.subject_id == subject_id, Score.semester_id == semester_id)
        .group_by(Student.id)
    ).subquery()

    weighted_avg_score = ((weighted_scores_subquery.c.total_weighted_score / weighted_scores_subquery.c.total_weight)
                          .label('avg_weighted_score')
                          )

    # Base query to retrieve classes and count of students
    base_query = (
        db.session.query(Class.id, Class.name, func.count(Student.id))
        .join(Teach)
        .join(StudentClass, Class.id == StudentClass.class_id, isouter=True)
        .join(Student, isouter=True)
        .filter(StudentClass.semester_id == semester.id)
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


def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)
