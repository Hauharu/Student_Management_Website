from xmlrpc.client import DateTime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, validates
from StudentManagement_Flask.ManageApp import db, app
from enum import Enum as UserEnum
from datetime import datetime
from flask_login import UserMixin


class UserGender(UserEnum):
    MALE = 0
    FEMALE = 1


class UserRole(UserEnum):
    ADMIN = 0
    STAFF = 1
    TEACHER = 2


class Grade(UserEnum):
    K10 = 10
    K11 = 11
    K12 = 12


class Semester(UserEnum):
    S1 = 1
    S2 = 2


class UserInformation(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum(UserGender))
    dateOfBirth = Column(Date, nullable=True)
    address = Column(String(255), nullable=False)
    phoneNumber = Column(String(15), nullable=False, unique=False)
    email = Column(String(255), nullable=False, unique=True)
    avatar = Column(String(255), nullable=True, default="")
    joined_date = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)


class User(UserInformation, UserMixin):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(255),
                    default="https://th.bing.com/th/id/R.dbc8e6138b38860cee6899eabc67df45?rik=hZCUMR4xQ%2btlBA&pid=ImgRaw&r=0")
    user_role = Column(Enum(UserRole), nullable=False)

    # admin = relationship('admin', backref='user', uselist=False)
    teacher = relationship('Teacher', backref='user', uselist=False)
    staff = relationship('Staff', backref='user', uselist=False)

    def __str__(self):
        return self.name


class Teacher(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    qualification = Column(String(20))

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)


# teach = relationship('Teach', backref='teacher', lazy=True)


# form_teacher = relationship('FormTeacher', backref='teacher', uselist=False, lazy=True)


class Staff(User):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)


class Student(UserInformation):
    # admission_date = Column(DateTime, default=datetime.now())
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_class = relationship('StudentClass', backref='student', lazy=True)


class Class(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)
    grade = Column(Enum(Grade))
    #  teach = relationship('Teach', backref='class', lazy=True)
    # form_teacher = relationship('FormTeacher', backref='class', uselist=False, lazy=True)
    student_class = relationship('StudentClass', backref='class', lazy=True)

    def __str__(self):
        return self.name


class Period(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester = Column(Enum(Semester))
    year = Column(String(4))
    #   teach = relationship('Teach', backref='period', lazy=True)
    # scores = relationship('Score', backref='period', lazy=True)
    #  form_teacher = relationship('FormTeacher', backref='period', uselist=False, lazy=True)
    student_class = relationship('StudentClass', backref='period', lazy=True)

    __table_args__ = (
        UniqueConstraint('semester', 'year', name='unique_semester_year'),
    )

    def __str__(self):
        return f'{"Học kì 1" if self.semester == Semester.SEMESTER_1 else "Học kì 2"} {self.year}'


class StudentClass(db.Model):
    student_id = Column(Integer, ForeignKey(Student.id), primary_key=True)
    class_id = Column(Integer, ForeignKey(Class.id), primary_key=True)
    period_id = Column(Integer, ForeignKey(Period.id), primary_key=True)


if __name__ == "__main__":
    with app.app_context():
             db.create_all()
        # c1 = Class(name='10A2', grade=Grade.K10)
        # c2 = Class(name='10B1', grade=Grade.K10)
        # c3 = Class(name='10C1', grade=Grade.K10)
        # c4 = Class(name='11A2', grade=Grade.K11)
        # c5 = Class(name='11B3', grade=Grade.K11)
        # c6 = Class(name='11C1', grade=Grade.K11)
        # c7 = Class(name='12A2', grade=Grade.K12)
        # c8 = Class(name='12B3', grade=Grade.K12)
        # c9 = Class(name='12C2', grade=Grade.K12)

        # db.session.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9])
        # db.session.commit()

        # p1 = Period(semester=Semester.S1, year='2024')
        # p2 = Period(semester=Semester.S2, year='2024')
        # db.session.add_all([p1, p2])
        # db.session.commit()

        # # thêm học sinh vào lớp
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




    # import json
    #
    # with open('data/students.json', encoding="utf-8") as f:
    #     students = json.load(f)
    #     for s in students:
    #         stud = Student(name=s['name'], gender=s['gender'],
    #                        address=s['address'],
    #                        phoneNumber=s['phone_number'], email=s['email'], avatar=s['avatar'])
    #         db.session.add(stud)
    #     db.session.commit()

    # import hashlib
    #
    # u1 = User(
    #     name='Nguyễn Trung Hậu',
    #     email='2251010027hau@ohs.edu.vn',
    #     username='admin',
    #     dateOfBirth=datetime.strptime('2004-01-01', '%Y-%m-%d').date(),
    #     password=str(hashlib.md5('123'.encode('utf8')).hexdigest()),
    #     user_role=UserRole.ADMIN,
    #     phoneNumber='12345678910',
    #     address='quan 1',
    #     gender=UserGender.MALE
    # )
    #
    # u2 = User(
    #     name='Phạm Nguyên Bảo',
    #     email='2251010010bao@ohs.edu.vn',
    #     username='teacher',
    #     dateOfBirth=datetime.strptime('2004-01-01', '%Y-%m-%d').date(),
    #     password=str(hashlib.md5('123'.encode('utf8')).hexdigest()),
    #     user_role=UserRole.TEACHER,
    #     phoneNumber='12345678321',
    #     address='quan 2',
    #     gender=UserGender.MALE
    # )
    #
    # u3 = User(
    #     name='Nguyễn Vũ Luân',
    #     email='2251050042luan@ohs.edu.vn',
    #     username='staff',
    #     dateOfBirth=datetime.strptime('2004-01-01', '%Y-%m-%d').date(),
    #     password=str(hashlib.md5('123'.encode('utf8')).hexdigest()),
    #     user_role=UserRole.STAFF,
    #     phoneNumber='12345678123',
    #     address='quan 1',
    #     gender=UserGender.MALE
    # )
    # db.session.add_all([u1, u2, u3])
    # db.session.commit()



