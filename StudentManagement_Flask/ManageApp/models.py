from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from ManageApp import db,app


# Bảng UserGender
class UserGender(db.Model):
    __tablename__ = 'UserGender'
    userGenderID = Column(Integer, primary_key=True, autoincrement=True)
    male = Column(Boolean, nullable=False)
    female = Column(Boolean, nullable=False)


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


# Bảng UserInformation
class UserInformation(db.Model):
    __tablename__ = 'UserInformation'
    userID = Column(Integer, primary_key=True, autoincrement=True)
    userName = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    dateOfBirth = Column(Date, nullable=False)
    address = Column(String(255), nullable=False)
    phoneNumber = Column(String(15), nullable=False)
    email = Column(String(255), nullable=False)
    userGenderID = Column(Integer, ForeignKey('UserGender.userGenderID'), nullable=False)
    userTypeID = Column(Integer, ForeignKey('UserType.userTypeID'), nullable=False)

    user_gender = relationship('UserGender', backref='users', lazy=True)
    user_type = relationship('UserType', backref='users', lazy=True)


# Bảng Student
class Student(db.Model):
    __tablename__ = 'Student'
    studentID = Column(Integer, primary_key=True, autoincrement=True)
    admission_date = Column(Date, nullable=False)
    ageID = Column(Integer, ForeignKey('Age.ageID'), nullable=False)

    age = relationship('Age', backref='students', lazy=True)


# Bảng Administrator
class Administrator(db.Model):
    __tablename__ = 'Administrator'
    adminID = Column(db.Integer, primary_key=True, autoincrement=True)
    isSupervisor = Column(db.Boolean, nullable=False)


# Bảng SchoolStaff
class SchoolStaff(db.Model):
    __tablename__ = 'SchoolStaff'
    staffID = Column(Integer, primary_key=True, autoincrement=True)
    isSupportStaff = Column(Boolean, nullable=False)


# Bảng Teacher
class Teacher(db.Model):
    __tablename__ = 'Teacher'
    teacherID = Column(Integer, primary_key=True, autoincrement=True)
    qualification = Column(String(255), nullable=False)
    isSubjectTeacher = Column(Boolean, nullable=False)


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


# Bảng Class_Student
class ClassStudent(db.Model):
    __tablename__ = 'Class_Student'
    studentID = Column(db.Integer, ForeignKey('Student.studentID'), primary_key=True)
    classID = Column(db.Integer, ForeignKey('Class.classID'), primary_key=True)


# Bảng Teacher_Subject
class TeacherSubject(db.Model):
    __tablename__ = 'Teacher_Subject'
    teacherID = Column(Integer, ForeignKey('Teacher.teacherID'), primary_key=True)
    subjectID = Column(Integer, ForeignKey('Subject.subjectID'), primary_key=True)


if __name__ == "__main__":
   with app.app_context():
         db.create_all()
