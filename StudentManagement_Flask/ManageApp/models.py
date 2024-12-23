import enum
import hashlib
from ManageApp import db, app
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Date, DateTime, CheckConstraint, \
    UniqueConstraint


################################################### Class Abstract #####################################################

# Abstract dùng để tạo tự động id người dùng và auto increase
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


##################################################### Class Enums ######################################################

class UserRole(enum.Enum):
    ADMIN = 1
    TEACHER = 2
    STAFF = 3

    def __str__(self):
        if str(self.name).__eq__('STAFF'):
            return 'NHÂN VIÊN NHÀ TRƯỜNG'
        elif str(self.name).__eq__('TEACHER'):
            return 'GIÁO VIÊN'
        else:
            return 'QUẢN TRỊ VIÊN'


class UserGender(enum.Enum):
    MALE = 'Nam'
    FEMALE = 'Nữ'


class StudentGrade(enum.Enum):
    GRADE_10TH = 10
    GRADE_11ST = 11
    GRADE_12ND = 12


class ScoreType(enum.Enum):
    EXAM_15MINS = 1
    EXAM_45MINS = 2
    EXAM_FINAL = 3


class Regulations(enum.Enum):
    Re_Age = 'QuyDinhTuoi'
    Re_quantity = 'QuyDinhSoLuong'


class SemesterType(enum.Enum):
    SEMESTER_1 = 1
    SEMESTER_2 = 2


######################################################## Classes #######################################################


class UserInformation(BaseModel):
    __tablename__ = 'user_information'
    name = Column(String(50), nullable=False)
    gender = Column(Enum(UserGender), default=UserGender.MALE)
    dateOfBirth = Column(Date, nullable=False)
    address = Column(String(255), nullable=False)
    phoneNumber = Column(String(10), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    joined_date = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("LENGTH(phoneNumber) = 10 AND phoneNumber REGEXP '^[0-9]+$'", name="check_phoneNumber_format"),
        CheckConstraint("email LIKE '%@%'", name="check_email_format")
    )

    def __str__(self):
        return self.name


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.TEACHER)
    is_supervisor = Column(Boolean, nullable=False, default=False)
    avatar = Column(String(255),
                    default="https://th.bing.com/th/id/R.dbc8e6138b38860cee6899eabc67df45?rik=hZCUMR4xQ%2btlBA&pid=ImgRaw&r=0")
    userInformation_id = Column(Integer, ForeignKey("user_information.id"), unique=True, nullable=False)
    userInformation = relationship("UserInformation", backref="user", lazy=True, uselist=False)
    classes = relationship("Class", backref="teacher", lazy=True)

    def __str__(self):
        return self.username


class Semester(BaseModel):
    __tablename__ = 'semester'
    semesterName = Column(String(50), nullable=False)
    year = Column(Integer, default=datetime.now().year)
    teach = relationship('Teach', backref='semesters', lazy=True)
    student = relationship("Student", backref="semestes", lazy=True)
    score = relationship("Score", backref="semesters", lazy=True)
    __table_args__ = (
        UniqueConstraint('semesterName', 'year', name='unique_semester_year'),
    )

    def __str__(self):
        return f'{"Học kì 1" if self.semesterName == SemesterType.SEMESTER_1 else "Học kì 2"} {self.year}'


class Student(BaseModel):
    __tablename__ = 'student'
    admission_date = Column(DateTime, default=datetime.now())
    grade = Column(Enum(StudentGrade), default=StudentGrade.GRADE_10TH)
    student_class = relationship('StudentClass', backref='student', lazy=True)
    score = relationship("Score", backref="student", lazy=True)
    userInformation = relationship("UserInformation", backref="student", lazy=True, uselist=False)
    userInformation_id = Column(Integer, ForeignKey("user_information.id"), unique=True, nullable=False)
    regulation_id = Column(Integer, ForeignKey('regulation.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)

    def __str__(self):
        return self.userInformation.name


class Subject(BaseModel):
    __tablename__ = 'subject'
    subjectName = Column(String(20), nullable=False)
    grade = Column(Enum(StudentGrade), default=StudentGrade.GRADE_10TH)
    exam_15mins = Column(Integer, nullable=False)
    exam_45mins = Column(Integer, nullable=False)
    exam_Final = Column(Integer, default=False)


class TeacherSubject(BaseModel):
    __tablename__ = 'teacher_subject'
    teacher_id = Column(Integer, ForeignKey(User.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    __table_args__ = (UniqueConstraint('teacher_id', 'subject_id'),)


__table_args__ = (
    CheckConstraint("exam_15mins >= 1 AND exam_15mins <=5", name="check_exam_15mins"),
    CheckConstraint("exam_45mins >= 1 AND exam_45mins <=3", name="check_exam_45mins"),
    UniqueConstraint('exam_Final', 'subjectName', name="check_exam_Final")
)


def __str__(self):
    return self.subjectName


class Class(BaseModel):
    __tablename__ = 'class'
    className = Column(String(50), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    grade = Column(Enum(StudentGrade))
    year = Column(Integer, default=datetime.now().year)
    teach = relationship('Teach', backref='class', lazy=True)
    teacher_id = Column(Integer, ForeignKey(User.id), unique=True)
    student_Class = relationship('StudentClass', backref='class', lazy=True)
    regulation_id = Column(Integer, ForeignKey('regulation.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('className', 'year'),
        CheckConstraint("quantity >= 0", name="check_quantity"),
    )

    def __str__(self):
        return self.className


class StudentClass(BaseModel):
    __tablename__ = 'student_class'
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    __table_args__ = (
        UniqueConstraint('class_id', 'student_id', name='unique_student_per_class'),
    )


class Teach(BaseModel):
    __tablename__ = 'teach'
    teacher_id = Column(Integer, ForeignKey(User.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('teacher_id', 'subject_id', 'class_id', 'semester_id', name='unique_teacher_assignment'),
    )


class ScoreDetail(BaseModel):
    __tablename__ = 'score_detail'
    score = Column(Float)
    type = Column(Enum(ScoreType))
    created_date = Column(DateTime, default=datetime.now())
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    scores = relationship("Score", backref="score_detail", lazy=True)
    student = relationship("Student", backref="score_detail", lazy=True)


class Score(BaseModel):
    __tablename__ = 'score'
    score = Column(Float)
    type = Column(Enum(ScoreType))
    count = Column(Integer)
    scoreDetail_id = Column(Integer, ForeignKey(ScoreDetail.id), nullable=False)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    __table_args__ = (UniqueConstraint('type', 'score', 'student_id',
                                       'semester_id', 'subject_id',
                                       name='_mark_subject_uc'),
                      CheckConstraint('score >= 0', name='check_score_min'),
                      CheckConstraint('score <= 10', name='check_score_max'),
                      )

    def __str__(self):
        return "{value} - {type} - {student} - {subject} - HK{semester}".format(value=self.value, type=self.type,
                                                                                student=self.student.name,
                                                                                subject=self.subject.subjectName,
                                                                                semester=self.semester.semesterName)


class Regulation(BaseModel):
    __tablename__ = 'regulation'
    regulationName = Column(String(100))
    content = Column(String(255))
    data = Column(Integer)
    min_value = Column(Integer, nullable=False)
    max_value = Column(Integer, nullable=False)
    type = Column(Enum(Regulations), default=Regulations.Re_Age)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime, default=datetime.now())
    classes = relationship('Class', backref='regulation', lazy=True)
    students = relationship('Student', backref='regulation', lazy=True)

    __table_args__ = (
        CheckConstraint("min_value <= max_value", name="check_min_max"),
    )

    def __str__(self):
        return self.regulationName

########################################################################################################################
if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        # db.create_all()

        # Tạo dữ liệu mẫu cho UserInformation
        user1 = UserInformation(
            name="Nguyễn Trung Hậu",
            gender=UserGender.MALE,
            dateOfBirth=None,
            address="Bến Tre",
            phoneNumber="0912345678",
            email="2251010027hau@osh.edu.vn"
        )
        user2 = UserInformation(
            name="Phạm Nguyên Bảo",
            gender=UserGender.MALE,
            dateOfBirth=None,
            address="Cần Thơ",
            phoneNumber="0912345679",
            email="2251010028bao@osh.edu.vn"
        )

        user3 = UserInformation(
            name="",
            gender=UserGender.MALE,
            dateOfBirth="None",
            address="Hà Nội",
            phoneNumber="0912345680",
            email="2251010029luan@osh.edu.vn"
        )

        user4 = UserInformation(
            name="Trần Xuân Đức",
            gender=UserGender.MALE,
            dateOfBirth=None,
            address="TP.Hồ Chí Minh",
            phoneNumber="0912345681",
            email="2251010030duc@osh.edu.vn"
        )

        user5 = UserInformation(
            name="Hứa Quang Đạt",
            gender=UserGender.MALE,
            dateOfBirth=None,
            address="Đà Nẵng",
            phoneNumber="0912345682",
            email="2251010026dat@osh.edu.vn"
        )

        user6 = UserInformation(
            name="Nguyễn Thị Kim Ngân",
            gender=UserGender.FEMALE,
            dateOfBirth=None,
            address="Hải Phòng",
            phoneNumber="0912345683",
            email="2251010023ngan@osh.edu.vn"
        )

        db.session.add_all([user1, user2 ,user3 ,user4 ,user5,user6])
        db.session.commit()
        # # Tạo dữ liệu mẫu cho User
        # user1 = User(
        #     username="admin",
        #     password=hashlib.sha256("admin123".encode('utf-8')).hexdigest(),
        #     user_role=UserRole.ADMIN,
        #     is_supervisor=True,
        #     userInformation=user_info1
        # )
        #
        # user2 = User(
        #     username="teacher1",
        #     password=hashlib.sha256("teacher123".encode('utf-8')).hexdigest(),
        #     user_role=UserRole.TEACHER,
        #     is_supervisor=False,
        #     userInformation=user_info2
        # )
        #
        # # Tạo dữ liệu mẫu cho Semester
        # semester1 = Semester(
        #     semesterName="SEMESTER_1",
        #     year=2024
        # )
        # semester2 = Semester(
        #     semesterName="SEMESTER_2",
        #     year=2024
        # )
        #
        # # Tạo dữ liệu mẫu cho Regulation
        # regulation1 = Regulation(
        #     regulationName="Quy định về tuổi học sinh",
        #     content="Độ tuổi học sinh phải từ 15 đến 18 tuổi.",
        #     data=None,
        #     min_value=15,
        #     max_value=18,
        #     type=Regulations.Re_Age
        # )
        #
        # regulation2 = Regulation(
        #     regulationName="Quy định về số lượng học sinh",
        #     content="Sĩ số tối đa của mỗi lớp không vượt quá 50.",
        #     data=None,
        #     min_value=1,
        #     max_value=50,
        #     type=Regulations.Re_quantity
        # )
        #
        # # Tạo dữ liệu mẫu cho Class
        # class1 = Class(
        #     className="10A1",
        #     quantity=45,
        #     grade=StudentGrade.GRADE_10TH,
        #     year=2024,
        #     teacher_id=1,  # ID của giáo viên
        #     regulation=regulation2
        # )
        #
        # # Tạo dữ liệu mẫu cho Student
        # student1 = Student(
        #     admission_date=datetime.now(),
        #     grade=StudentGrade.GRADE_10TH,
        #     userInformation=user_info1,
        #     regulation=regulation1,
        #     semester=semester1
        # )
        #
        # student2 = Student(
        #     admission_date=datetime.now(),
        #     grade=StudentGrade.GRADE_11ST,
        #     userInformation=user_info2,
        #     regulation=regulation1,
        #     semester=semester2
        # )
        #
        # # Tạo dữ liệu mẫu cho Subject
        # subject1 = Subject(
        #     subjectName="Toán",
        #     grade=StudentGrade.GRADE_10TH,
        #     exam_15mins=3,
        #     exam_45mins=2,
        #     exam_Final=1
        # )
        #
        # subject2 = Subject(
        #     subjectName="Vật Lý",
        #     grade=StudentGrade.GRADE_10TH,
        #     exam_15mins=2,
        #     exam_45mins=1,
        #     exam_Final=1
        # )
        #
        # # Thêm dữ liệu vào database
        # db.session.add_all([user_info1, user_info2, user1, user2, semester1, semester2,
        #                     regulation1, regulation2, class1, student1, student2, subject1, subject2])
        # db.session.commit()
