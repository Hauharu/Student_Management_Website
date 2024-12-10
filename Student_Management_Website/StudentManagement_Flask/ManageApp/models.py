from xmlrpc.client import DateTime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from ManageApp import db,app
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


class UserInformation(db.Model):
    __abstract__ = True

    name = Column(String(50), nullable=False)
    gender = Column(Enum(UserGender))
    dateOfBirth = Column(Date, nullable=False)
    address = Column(String(255), nullable=False)
    phoneNumber = Column(String(15), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    joined_date = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)


class User(UserInformation, UserMixin):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(255), default="https://th.bing.com/th/id/R.dbc8e6138b38860cee6899eabc67df45?rik=hZCUMR4xQ%2btlBA&pid=ImgRaw&r=0")
    user_role = Column(Enum(UserRole), nullable=False)

    def __str__(self):
        return self.name



# Bảng UserType
class UserType(db.Model):
    __tablename__ = 'UserType'
    userTypeID = Column(Integer, primary_key=True, autoincrement=True)
    administrator = Column(Boolean, nullable=False)
    teacher = Column(Boolean, nullable=False)
    schoolStaff = Column(Boolean, nullable=False)
    student = Column(Boolean, nullable=False)


# Bảng Age
class Age(db.Model):
    __tablename__ = 'Age'
    ageID = Column(Integer, primary_key=True, autoincrement=True)
    minAge = Column(Integer, nullable=False)
    maxAge = Column(Integer, nullable=False)


# Bảng Student
class Student(db.Model):
    __tablename__ = 'Student'
    studentID = Column(Integer, primary_key=True, autoincrement=True)
    admission_date = Column(Date, nullable=False)
    ageID = Column(Integer, ForeignKey('Age.ageID'), nullable=False)

    age = relationship('Age', backref='students', lazy=True)


# Bảng Administrator
class Admin(db.Model):
    __tablename__ = 'Admin'
    adminID = Column(Integer, ForeignKey(User.id), primary_key=True)


class Teacher(db.Model):
    __tablename__ = 'Teacher'
    teacherID = Column(Integer, ForeignKey(User.id), primary_key=True)


class SchoolStaff(db.Model):
    __tablename__ = 'SchoolStaff'
    staffID = Column(Integer, ForeignKey(User.id), primary_key=True)


# Bảng PhoneNumber
class PhoneNumber(db.Model):
    __tablename__ = 'PhoneNumber'
    phoneNumberID = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String(15), nullable=False)
    studentID = Column(Integer, ForeignKey('Student.studentID'), nullable=True)
    teacherID = Column(Integer, ForeignKey('Teacher.teacherID'), nullable=True)
    schoolStaffID = Column(Integer, ForeignKey('SchoolStaff.staffID'), nullable=True)


# Bảng Class
class Class(db.Model):
    __tablename__ = 'Class'
    classID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    unit = Column(String(255), nullable=False)
    gradeID = Column(Integer, ForeignKey('StudentGrade.gradeID'), nullable=False)

    grade = relationship('StudentGrade', backref='classes', lazy=True)


# Bảng StudentGrade
class StudentGrade(db.Model):
    __tablename__ = 'StudentGrade'
    gradeID = Column(Integer, primary_key=True, autoincrement=True)
    grade_10 = Column(Boolean, nullable=False)
    grade_11 = Column(Boolean, nullable=False)
    grade_12 = Column(Boolean, nullable=False)


# Bảng Subject
class Subject(db.Model):
    __tablename__ = 'Subject'
    subjectID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    exam_15mins = Column(Float, nullable=False)
    exam_45mins = Column(Float, nullable=False)
    finalExam = Column(Float, nullable=False)


# Bảng ScoreType
class ScoreType(db.Model):
    __tablename__ = 'ScoreType'
    scoreTypeID = Column(Integer, primary_key=True, autoincrement=True)
    exam_15mins = Column(Boolean, nullable=False)
    exam_45mins = Column(Boolean, nullable=False)
    finalExam = Column(Boolean, nullable=False)


# Bảng Period
class Period(db.Model):
    __tablename__ = 'Period'
    periodID = Column(Integer, primary_key=True, autoincrement=True)
    semesterID = Column(Integer, ForeignKey('Semester.semesterID'), nullable=False)
    year = Column(Integer, nullable=False)

    semester = relationship('Semester', backref='periods', lazy=True)


# Bảng Semester
class Semester(db.Model):
    __tablename__ = 'Semester'
    semesterID = Column(Integer, primary_key=True, autoincrement=True)
    semester_1 = Column(Boolean, nullable=False)
    semester_2 = Column(Boolean, nullable=False)


# Bảng Score
class Score(db.Model):
    __tablename__ = 'Score'
    scoreID = Column(Integer, primary_key=True, autoincrement=True)
    studentID = Column(Integer, ForeignKey('Student.studentID'), nullable=False)
    subjectID = Column(Integer, ForeignKey('Subject.subjectID'), nullable=False)
    periodID = Column(Integer, ForeignKey('Period.periodID'), nullable=False)

    student = relationship('Student', backref='scores', lazy=True)
    subject = relationship('Subject', backref='scores', lazy=True)
    period = relationship('Period', backref='scores', lazy=True)


# Bảng ScoreDetail
class ScoreDetail(db.Model):
    __tablename__ = 'ScoreDetail'
    scoreDetailID = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(Float, nullable=False)
    scoreTypeID = Column(Integer, ForeignKey('ScoreType.scoreTypeID'), nullable=False)
    scoreID = Column(Integer, ForeignKey('Score.scoreID'), nullable=False)

    score_type = db.relationship('ScoreType', backref='score_details', lazy=True)
    scores = relationship('Score', backref='score_details', lazy=True)


# Bảng Class_Teacher
class ClassTeacher(db.Model):
    __tablename__ = 'Class_Teacher'
    classID = Column(Integer, ForeignKey('Class.classID'), primary_key=True)
    teacherID = Column(Integer, ForeignKey('Teacher.teacherID'), primary_key=True)


# Bảng Teacher_Subject
class TeacherSubject(db.Model):
    __tablename__ = 'Teacher_Subject'
    teacherID = Column(Integer, ForeignKey('Teacher.teacherID'), primary_key=True)
    subjectID = Column(Integer, ForeignKey('Subject.subjectID'), primary_key=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # import hashlib
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
