import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date, Enum, DateTime, CheckConstraint, func
from sqlalchemy.orm import relationship, backref
from ManageApp import db, app
from datetime import datetime
from flask_login import UserMixin


####################################### Class Abstract không tạo ra bảng csdl ##########################################

# Class Abstract sẽ tự động cập nhật id người dùng và auto increase
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


########################################## Class Enum không tạo ra bảng csdl ###########################################

# Class Enum về giới tính
class UserGender(enum.Enum):
    MALE = 'Nam'
    FEMALE = 'Nữ'


# Class Enum về vai trò người dùng
class UserRole(enum.Enum):
    ADMIN = 1
    TEACHER = 2
    STAFF = 3


# Class Enum Khối
class StudentGrade(enum.Enum):
    GRADE_10TH = 10
    GRADE_11ST = 11
    GRADE_12ND = 12


# Class Enum về loại điểm kiểm tra
class ScoreType(enum.Enum):
    EXAM_15MINS = 1
    EXAM_45MINS = 2
    EXAM_FINAL = 3


# Class Enum về quy định độ tuổi hs và số lượng hs trong một lớp
class Regulations(enum.Enum):
    Re_Age = 'QuyDinhTuoi'
    Re_quantity = 'QuyDinhSoLuong'


############################################### Các Class sẽ tạo ra bảng csdl ##########################################

# Bảng thông tin cơ bản của 1 người dùng
class Information(BaseModel):
    name = Column(String(50), nullable=False)
    gender = Column(Enum(UserGender), default=UserGender.MALE)
    dateOfBirth = Column(Date, nullable=True)
    address = Column(String(255), nullable=False)
    phoneNumber = Column(String(15), nullable=False, unique=False)
    email = Column(String(255), nullable=False, unique=True)
    joined_date = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)
    # check xem dateOfBirth có là tương lai, phoneNumber chỉ là số, email phải có @
    __table_args__ = (
        CheckConstraint("LENGTH(phoneNumber) = 11 AND phoneNumber REGEXP '^[0-9]+$'", name="check_phoneNumber_format"),
        CheckConstraint("email LIKE '%@%'", name="check_email_format")
    )

    def __str__(self):
        return self.name


# Bảng cá nhân người dùng
class User(BaseModel, UserMixin):
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.TEACHER)
    is_supervisor = Column(Boolean, nullable=False, default=False)
    avatar = Column(String(255),
                    default="https://th.bing.com/th/id/R.dbc8e6138b38860cee6899eabc67df45?rik=hZCUMR4xQ%2btlBA&pid=ImgRaw&r=0")
    information_id = Column(Integer, ForeignKey("information.id"), unique=True, nullable=False)
    information = relationship("Information", backref="user", lazy=True, uselist=False)

    admin = relationship('Admin', backref='user', uselist=False)
    teacher = relationship('Teacher', backref='user', uselist=False)
    staff = relationship('Staff', backref='user', uselist=False)

    def __str__(self):
        return self.username


class Subject(BaseModel):
    name = Column(String(20), nullable=False)
    grade = Column(Enum(StudentGrade), default=StudentGrade.GRADE_10TH)
    exam_15mins = Column(Integer, nullable=False)
    exam_45mins = Column(Integer, nullable=False)
    # check điểm 15p tối thểu 1 <= 5 bài, điểm 45p tối thiểu là 1 <=3 bài
    __abstract__ = __table_args__ = (
        CheckConstraint("exam_15mins >= 1 AND exam_15mins <=5", name="check_exam_15mins"),
        CheckConstraint("exam_45mins >= 1 AND exam_45mins <=3 ", name="check_exam_45mins"),
    )


class Class(BaseModel):
    name = Column(String(10), nullable=False)
    grade = Column(Enum(StudentGrade))
    quantity = Column(Integer, default=0)
    year = Column(Integer, default=datetime.now().year)
    teach = relationship('Teach', backref='class', lazy=True)
    student_class = relationship('StudentClass', backref='class', lazy=True)
    regulation_id = Column(Integer, ForeignKey('regulation.id'), nullable=False)
    # check xem lớp có số lượng bao nhiêu hs
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity"),
    )

    def __str__(self):
        return self.name


# Bảng học sinh
class Student(BaseModel):
    admission_date = Column(DateTime, default=datetime.now())
    grade = Column(Enum(StudentGrade), default=StudentGrade.GRADE_10TH)
    student_class = relationship('StudentClass', backref='student', lazy=True)
    information = relationship("Information", backref="student", lazy=True, uselist=False)
    information_id = Column(Integer, ForeignKey("information.id"), unique=True, nullable=False)
    regulation_id = Column(Integer, ForeignKey('regulation.id'), nullable=False)

    def __str__(self):
        return self.information.name


# Bảng Admin
class Admin(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    information = relationship("Information", backref="student", lazy=True, uselist=False)
    information_id = Column(Integer, ForeignKey("information.id"), unique=True, nullable=False)


# Bảng Teacher
class Teacher(BaseModel):
    qualification = Column(String(20))
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    teach = relationship('Teach', backref='teacher', lazy=True)
    information = relationship("Information", backref="student", lazy=True, uselist=False)
    information_id = Column(Integer, ForeignKey("information.id"), unique=True, nullable=False)


class Staff(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    information = relationship("Information", backref="student", lazy=True, uselist=False)
    information_id = Column(Integer, ForeignKey("information.id"), unique=True, nullable=False)


class Semester(BaseModel):
    semester_name = Column(String(50), nullable=False)
    year = Column(Integer, default=datetime.now().year)
    __table_args__ = (
        db.UniqueConstraint('semester_name', 'year', name='unique_semester'),
    )

    def __str__(self):
        return f"< {self.semester_name} - {self.year}"


class Period(BaseModel):
    semester = relationship('Semester', backref='Period', lazy=True)
    year = Column(String(4))
    teach = relationship('Teach', backref='period', lazy=True)
    scores = relationship('Score', backref='period', lazy=True)
    student_class = relationship('StudentClass', backref='period', lazy=True)
    qualification = Column(Integer, ForeignKey('regulation.id'), nullable=False)

    def __str__(self):
        return f'{"Học kì 1" if self.semester == Semester.SEMESTER_1 else "Học kì 2"} {self.year}'


class Teach(BaseModel):
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    period_id = Column(Integer, ForeignKey(Period.id), nullable=False)
    semester_id = Column(Integer, ForeignKey(Semester.id), nullable=False)

    period = relationship('Period', backref='teach', lazy=True)
    classes = relationship('Class', backref='teach', lazy=True)
    semester = relationship('Semester', backref='teach', lazy=True)
    subject = relationship('Subject', backref='teach', lazy=True)
    teacher = relationship('User', backref='teach', lazy=True)

    def __str__(self):
        return f"Lớp: {self.classes.name}, {self.semester.semester_name}, Giáo viên: {self.teacher.information.name}"


class ScoreDetail(BaseModel):
    score = Column(Float)
    type = Column(Enum(ScoreType))
    created_date = Column(DateTime, default=datetime.now())


class Score(BaseModel):
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    score_detail_id = Column(Integer, ForeignKey(ScoreDetail.id), nullable=False)
    period_id = Column(Integer, ForeignKey(Period.id), nullable=False)
    __table_args__ = (
        CheckConstraint('score >= 0', name='check_age_min'),
        CheckConstraint('score <= 10', name='check_age_max'),
    )


class regulation(BaseModel):
    name = Column(String(100))
    content = Column(String(255))
    data = Column(Integer)
    type = Column(Enum(Regulations), default=Regulations.Re_Age)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())

    def __str__(self):
        return self.name


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    #
    # import json
    #
    # with open('data/student.json', encoding="utf-8") as f:
    #     students = json.load(f)
    #     for s in students:
    #         stud = Student(first_name=s['first_name'], last_name=s['last_name'], gender=s['gender'],
    #                        address=s['address'],
    #                        phone_number=s['phone_number'], email=s['email'], avatar=s['avatar'])
    #         db.session.add(stud)
    #     db.session.commit()

import hashlib
# u = User(first_name='', username='admin1',
#          password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
#          user_role=UserRole.ADMIN, is_supervisor=True)
# db.session.add(u)
#
# u2 = User(username='kiet', user_role=UserRole.TEACHER, is_supervisor=False, first_name='Kiet',
#           last_name='Nguyen',
#           gender=UserGender.MALE, address='HCM', phone_number='0923740834', email='kiet@gmail.com',
#           avatar='https://res-console.cloudinary.com/dwdvnztnn/thumbnails/v1/image/upload/v1715050270/c3Vwcl9jYXRfZ3l0eGR5/drilldown',
#           password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
#
# db.session.add(u2)
# db.session.commit()
# admin = Admin(user_id=1)
#
# teacher = Teacher(qualification="Tiến sĩ", user_id=2)
# db.session.add_all([admin, teacher])
# db.session.commit()
# c1 = Class(name='10A2', grade=StudentGrade.GRADE_10TH)
# c2 = Class(name='10B1', grade=StudentGrade.GRADE_10TH)
# c3 = Class(name='10C1', grade=StudentGrade.GRADE_10TH)
# c4 = Class(name='11A2', grade=StudentGrade.GRADE_11ST)
# c5 = Class(name='11B3', grade=StudentGrade.GRADE_11ST)
# c6 = Class(name='11C1', grade=StudentGrade.GRADE_11ST)
# c7 = Class(name='12A2', grade=StudentGrade.GRADE_12ND)
# c8 = Class(name='12B3', grade=StudentGrade.GRADE_12ND)
# c9 = Class(name='12C2', grade=StudentGrade.GRADE_12ND)
#
# db.session.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9])
# db.session.commit()
#
#
# subj1 = Subject(name='Toán 10', grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=1)
# subj2 = Subject(name='Toán 11', grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=1)
# subj3 = Subject(name='Toán 12', grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1)
#
# subj4 = Subject(name='Sinh 10', grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=1)
# subj5 = Subject(name='Sinh 11', grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=1)
# subj6 = Subject(name='Sinh 12', grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1)
#
# subj7 = Subject(name='Văn 10', grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=1)
# subj8 = Subject(name='Văn 11', grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=1)
# subj9 = Subject(name='Văn 12', grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1)
# db.session.add_all([subj1, subj2, subj3, subj4, subj5, subj6, subj7, subj8, subj9])
# db.session.commit()
#
# p1 = Period(semester=Semester.SEMESTER_1, year='2024')
# p2 = Period(semester=Semester.SEMESTER_2, year='2024')
# db.session.add_all([p1,p2])
# db.session.commit()
#
# ft = FormTeacher(teacher_id=1, class_id=1, period_id=1)
# ft1 = FormTeacher(teacher_id=1, class_id=1, period_id=2)
# db.session.add_all([ft, ft1])
# db.session.commit()
#
# #thêm học sinh vào lớp
# sc = StudentClass(student_id=3, class_id=1)
# sc1 = StudentClass(student_id=4, class_id=1)
# sc2 = StudentClass(student_id=5, class_id=1)
# sc3 = StudentClass(student_id=6, class_id=1)
# sc4 = StudentClass(student_id=7, class_id=1)
# sc5 = StudentClass(student_id=8, class_id=1)
# sc6 = StudentClass(student_id=9, class_id=1)
# sc7 = StudentClass(student_id=10, class_id=1)
# sc8 = StudentClass(student_id=11, class_id=1)
# sc9 = StudentClass(student_id=12, class_id=1)
# #
# db.session.add_all([sc, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9])
# db.session.commit()
#
# sc = StudentClass(student_id=13, class_id=2)
# sc1 = StudentClass(student_id=14, class_id=2)
# sc2 = StudentClass(student_id=15, class_id=2)
# sc3 = StudentClass(student_id=16, class_id=2)
# sc4 = StudentClass(student_id=17, class_id=2)
# sc5 = StudentClass(student_id=18, class_id=2)
# sc6 = StudentClass(student_id=19, class_id=2)
# sc7 = StudentClass(student_id=20, class_id=2)
# sc8 = StudentClass(student_id=21, class_id=2)
# sc9 = StudentClass(student_id=22, class_id=2)
#
# db.session.add_all([sc, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9])
# db.session.commit()
#
# #thêm dữ liệu lớp teach
# t = Teach(teacher_id=1, subject_id=1, class_id=1, period_id=1)
# t1 = Teach(teacher_id=1, subject_id=1, class_id=1, period_id=2)
# t2 = Teach(teacher_id=1, subject_id=1, class_id=4, period_id=1)
# t3 = Teach(teacher_id=1, subject_id=1, class_id=4, period_id=2)
# db.session.add_all([t, t1, t2, t3])
# db.session.commit()
#
# db.session.commit()
#
#
