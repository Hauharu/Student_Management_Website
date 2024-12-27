import enum
import hashlib
from ManageApp import db, app
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Date, DateTime, CheckConstraint, \
    UniqueConstraint


################################################### Class Abstract #####################################################


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
    dateOfBirth = Column(DateTime, nullable=False)
    address = Column(String(255), nullable=False)
    phoneNumber = Column(String(10), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    joined_date = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("LENGTH(phoneNumber) = 10 AND phoneNumber REGEXP '^[0-9]+$'", name="check_phoneNumber"),
        CheckConstraint("email LIKE '%@%'", name="check_email")
    )

    def __str__(self):
        return self.name


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.TEACHER)
    avatar = Column(String(255),
                    default="https://th.bing.com/th/id/R.dbc8e6138b38860cee6899eabc67df45?rik=hZCUMR4xQ%2btlBA&pid=ImgRaw&r=0")
    userInformation_id = Column(Integer, ForeignKey("user_information.id"), unique=True, nullable=False)
    userInformation = relationship("UserInformation", backref="user", lazy=True, uselist=False)
    classes = relationship("Class", backref="teacher", lazy=True)

    def __str__(self):
        return self.username


class Student(BaseModel):
    __tablename__ = 'student'
    name = Column(String(50), nullable=False)
    # last_name = Column(String(50), nullable=False)
    gender = Column(Enum(UserGender), default=UserGender.MALE)
    dateOfBirth = Column(DateTime, nullable=False)
    address = Column(String(255), nullable=False)
    phoneNumber = Column(String(10), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    admission_date = Column(DateTime, default=datetime.now())
    grade = Column(Enum(StudentGrade), default=StudentGrade.GRADE_10TH)
    student_class = relationship('StudentClass', backref='student', lazy=True)
    score = relationship("Score", backref="student", lazy=True)
    regulation_id = Column(Integer, ForeignKey('regulation.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Semester(BaseModel):
    __tablename__ = 'semester'
    semester = Column(String(50), nullable=False)
    year = Column(Integer, default=datetime.now().year)
    teach = relationship('Teach', backref='semester', lazy=True)
    student = relationship("Student", backref="semester", lazy=True)
    score = relationship("Score", backref="semester", lazy=True)
    student_class = relationship('StudentClass', backref='semester', lazy=True)
    __table_args__ = (
        UniqueConstraint('semester', 'year', name='unique_semester_year'),
    )

    def __str__(self):
        return f'{"Học kì 1" if self.semester == SemesterType.SEMESTER_1 else "Học kì 2"} {self.year}'


class Subject(BaseModel):
    __tablename__ = 'subject'
    subjectName = Column(String(20), nullable=False)
    grade = Column(Enum(StudentGrade), default=StudentGrade.GRADE_10TH)
    exam_15mins = Column(Integer, nullable=False)
    exam_45mins = Column(Integer, nullable=False)
    exam_Final = Column(Integer, default=False)

    __table_args__ = (
        CheckConstraint("exam_15mins >= 1 AND exam_15mins <=5", name="check_exam_15mins"),
        CheckConstraint("exam_45mins >= 1 AND exam_45mins <=3", name="check_exam_45mins"),
        UniqueConstraint('exam_Final', 'subjectName', name="check_exam_Final")
    )

    def __str__(self):
        return self.subjectName


class TeacherSubject(BaseModel):
    __tablename__ = 'teacher_subject'
    teacher_id = Column(Integer, ForeignKey(User.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)

    __table_args__ = (UniqueConstraint('teacher_id', 'subject_id'),)


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
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('class_id', 'student_id','semester_id', name='unique_student_per_class'),
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


class Score(BaseModel):
    __tablename__ = 'score'
    score = Column(Float)
    type = Column(Enum(ScoreType))
    count = Column(Integer)
    scoreDetail_id = Column(Integer, ForeignKey('score_detail.id'), nullable=False)
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
                                                                                semester=self.semester.semester)


class ScoreDetail(BaseModel):
    __tablename__ = 'score_detail'
    score = Column(Float)
    type = Column(Enum(ScoreType))
    created_date = Column(DateTime, default=datetime.now())
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    scores = relationship("Score", backref="score_detail", lazy=True)
    student = relationship("Student", backref="score_detail", lazy=True)


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
         #db.drop_all()
        db.create_all()

        # CHẠY TỪNG BẢNG DỮ LIỆU, CHẠY CẢ 2 BẢNG DỮ LIỆU SCOREDETAIL VÀ SCORE

        ##Tạo dữ liệu mẫu cho UserInformation
        # user_info1 = UserInformation(
        #     name="Nguyễn Văn A", gender=UserGender.MALE, dateOfBirth=datetime(1990, 5, 15), address="Bến Tre",
        #     phoneNumber="0123765789", email="nguyenvana@osh.edu.vn")
        # user_info2 = UserInformation(
        #     name="Trần Thị B", gender=UserGender.FEMALE, dateOfBirth=datetime(1992, 7, 20), address="Trà Vinh",
        #     phoneNumber="0234567890", email="tranthib@osh.edu.vn")
        # user_info3 = UserInformation(
        #     name="Phan Thị C", gender=UserGender.FEMALE, dateOfBirth=datetime(1985, 3, 30), address="Đồng Tháp",
        #     phoneNumber="0345678901", email="phanthic@osh.edu.vn")
        # user_info4 = UserInformation(
        #     name="Trần Xuân D", gender=UserGender.MALE, dateOfBirth=datetime(1988, 11, 10), address="An Giang",
        #     phoneNumber="0456789012", email="tranxuand@osh.edu.vn")
        # user_info5 = UserInformation(
        #     name="Lương Xuân E", gender=UserGender.MALE, dateOfBirth=datetime(1995, 1, 25), address="Bạc Liêu",
        #     phoneNumber="0456789636", email="luongxuane@osh.edu.vn")
        # user_info6 = UserInformation(
        #     name="Lê Đức F", gender=UserGender.MALE, dateOfBirth=datetime(1995, 6, 26), address="Long An",
        #     phoneNumber="0123789636", email="leducf@osh.edu.vn")
        # db.session.add_all([user_info1, user_info2, user_info3, user_info4, user_info5, user_info6])
        # db.session.commit()

        # Tạo dữ liệu mẫu cho User
        # user1 = User(
        #     username="2251010001", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #     user_role=UserRole.ADMIN, userInformation_id=1)
        #
        # user2 = User(
        #     username="2251010002", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #     user_role=UserRole.ADMIN, userInformation_id=2
        # )
        #
        # user3 = User(
        #     username="2251010003", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #     user_role=UserRole.STAFF, userInformation_id=5
        # )
        # user4 = User(
        #     username="2251010004", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #     user_role=UserRole.STAFF, userInformation_id=6
        # )
        # user5 = User(
        #     username="2251010005", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #     user_role=UserRole.TEACHER, userInformation_id=3
        # )
        #
        # user6 = User(
        #     username="2251010006", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #     user_role=UserRole.TEACHER, userInformation_id=4
        # )
        #
        # db.session.add_all([user1, user2, user3, user4, user5, user6])
        # db.session.commit()

        # Tạo dữ liệu mẫu cho Semester
        # semester1 = Semester(
        #     semester="SEMESTER_1", year=2024)
        # semester2 = Semester(
        #     semester="SEMESTER_2", year=2024)
        # db.session.add_all([semester1, semester2])
        # db.session.commit()

        # Tạo dữ liệu mẫu cho Regulation
        # regulation1 = Regulation(
        #     regulationName="Quy định về tuổi học sinh", content="Độ tuổi học sinh phải từ 15 đến 20 tuổi.", data=None,
        #     min_value=15, max_value=20, type=Regulations.Re_Age
        # )
        #
        #
        # regulation2 = Regulation(
        #     regulationName="Quy định về số lượng học sinh", content="Sĩ số tối đa của mỗi lớp không vượt quá 40.",
        #     data=None, min_value=0, max_value=40, type=Regulations.Re_quantity
        # )
        # db.session.add_all([regulation1, regulation2])
        # db.session.commit()

        # Tạo dữ liệu mẫu cho Student
        # student1 = Student(
        #     name="Trần Lan", gender=UserGender.FEMALE, dateOfBirth=datetime(2007, 4, 20),
        #     address="Trà Vinh", phoneNumber="0789012345", email="lantran@osh.edu.vn", grade=StudentGrade.GRADE_11ST,
        #     regulation_id=1, semester_id=1
        # )
        #
        # student2 = Student(
        #     name="Lê Hoa", gender=UserGender.FEMALE, dateOfBirth=datetime(2009, 2, 10),
        #     address="Đồng Tháp", phoneNumber="0890123456", email="hoale@osh.edu.vn", grade=StudentGrade.GRADE_12ND,
        #     regulation_id=1, semester_id=1
        # )
        #
        # student3 = Student(
        #     name="Phạm Nam", gender=UserGender.MALE, dateOfBirth=datetime(2008, 5, 5),
        #     address="An Giang", phoneNumber="0901234567", email="nampham@osh.edu.vn", grade=StudentGrade.GRADE_10TH,
        #     regulation_id=1, semester_id=1
        # )
        #
        # student4 = Student(
        #     name="Hoàng Hương", gender=UserGender.FEMALE, dateOfBirth=datetime(2007, 10, 10),
        #     address="Bạc Liêu", phoneNumber="0912345678", email="huonghoang@osh.edu.vn", grade=StudentGrade.GRADE_11ST,
        #     regulation_id=1, semester_id=1
        # )
        #
        # student5 = Student(
        #     name="Ngô Phúc", gender=UserGender.MALE, dateOfBirth=datetime(2006, 12, 15),
        #     address="Cà Mau", phoneNumber="0923456789", email="phucngo@osh.edu.vn", grade=StudentGrade.GRADE_12ND,
        #     regulation_id=1, semester_id=1
        # )
        #
        # student6 = Student(
        #     name="Dương Mai", gender=UserGender.FEMALE, dateOfBirth=datetime(2008, 9, 25),
        #     address="Hậu Giang", phoneNumber="0934567890", email="maiduong@osh.edu.vn", grade=StudentGrade.GRADE_10TH,
        #     regulation_id=1, semester_id=1
        # )
        # db.session.add_all([student1, student2, student3, student4, student5, student6])
        # db.session.commit()

        # Tạo dữ liệu mẫu cho Subject
        # subject1 = Subject(subjectName="Toán", grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=2,
        #                    exam_Final=1)
        # subject2 = Subject(subjectName="Vật Lý", grade=StudentGrade.GRADE_11ST, exam_15mins=3, exam_45mins=2,
        #                    exam_Final=1)
        # subject3 = Subject(subjectName="Hóa Học", grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1,
        #                    exam_Final=1)
        # subject4 = Subject(subjectName="Sinh Học", grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=2,
        #                    exam_Final=1)
        # subject5 = Subject(subjectName="Tiếng Anh", grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=2,
        #                    exam_Final=1)
        # subject6 = Subject(subjectName="Ngữ Văn", grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=1,
        #                    exam_Final=1)
        # subject7 = Subject(subjectName="Lịch Sử", grade=StudentGrade.GRADE_11ST, exam_15mins=3, exam_45mins=2,
        #                    exam_Final=1)
        # subject8 = Subject(subjectName="Địa Lý", grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1,
        #                    exam_Final=1)
        # subject9 = Subject(subjectName="Giáo Dục Công Dân", grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=2,
        #                    exam_Final=1)
        # subject10 = Subject(subjectName="Tin Học", grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=1,
        #                     exam_Final=1)
        # db.session.add_all(
        #     [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10])
        # db.session.commit()

        # Tạo dữ liệu mẫu cho Class
        # class1 = Class(
        #     className="10C1", quantity=40, grade=StudentGrade.GRADE_10TH, year=2024, teacher_id=3, regulation_id=2)
        # class2 = Class(
        #     className="11C1", quantity=35, grade=StudentGrade.GRADE_11ST, year=2024, teacher_id=4, regulation_id=2)
        # class3 = Class(
        #     className="12C1", quantity=30, grade=StudentGrade.GRADE_12ND, year=2024, teacher_id=5, regulation_id=2)
        # db.session.add_all([class1, class2, class3])
        # db.session.commit()

        # # Tạo dữ liệu mẫu cho ScoreDetail
        # score_detail1 = ScoreDetail(score=10.0, type=ScoreType.EXAM_15MINS, created_date=datetime.now(), student_id=1)
        # score_detail2 = ScoreDetail(score=8.0, type=ScoreType.EXAM_45MINS, created_date=datetime.now(), student_id=2)
        # score_detail3 = ScoreDetail(score=7.0, type=ScoreType.EXAM_FINAL, created_date=datetime.now(), student_id=3)
        # score_detail4 = ScoreDetail(score=6.5, type=ScoreType.EXAM_15MINS, created_date=datetime.now(), student_id=4)
        # score_detail5 = ScoreDetail(score=6.0, type=ScoreType.EXAM_FINAL, created_date=datetime.now(), student_id=5)
        # score_detail6 = ScoreDetail(score=9.0, type=ScoreType.EXAM_45MINS, created_date=datetime.now(), student_id=6)
        # db.session.add_all([score_detail1, score_detail2, score_detail3, score_detail4, score_detail5, score_detail6])
        # db.session.commit()
        #
        # ## Tạo dữ liệu mẫu cho Score
        # score1 = Score(
        #     score=10.0, type=ScoreType.EXAM_15MINS, count=1, scoreDetail_id=score_detail1.id, student_id=1,
        #     semester_id=1, subject_id=1
        # )
        # score2 = Score(
        #     score=8.0, type=ScoreType.EXAM_45MINS, count=1, scoreDetail_id=score_detail2.id, student_id=2,
        #     semester_id=1, subject_id=2
        # )
        # score3 = Score(
        #     score=7.0, type=ScoreType.EXAM_FINAL, count=1, scoreDetail_id=score_detail3.id, student_id=3, semester_id=1,
        #     subject_id=3
        # )
        # score4 = Score(
        #     score=6.5, type=ScoreType.EXAM_15MINS, count=1, scoreDetail_id=score_detail4.id, student_id=4,
        #     semester_id=1, subject_id=4
        # )
        # score5 = Score(
        #     score=6.0, type=ScoreType.EXAM_FINAL, count=1, scoreDetail_id=score_detail5.id, student_id=5, semester_id=1,
        #     subject_id=5
        # )
        # score6 = Score(
        #     score=9.0, type=ScoreType.EXAM_45MINS, count=1, scoreDetail_id=score_detail6.id, student_id=6,
        #     semester_id=1, subject_id=6
        # )
        # db.session.add_all([score1, score2, score3, score4, score5, score6])
        # db.session.commit()

         # student_class1 = StudentClass(student_id=1, class_id=1, semester_id=1)
         # student_class2 = StudentClass(student_id=2, class_id=1, semester_id=1)
         # student_class3 = StudentClass(student_id=3, class_id=2, semester_id=1)
         # student_class4 = StudentClass(student_id=4, class_id=2, semester_id=1)
         # student_class5 = StudentClass(student_id=5, class_id=3, semester_id=1)
         # student_class6 = StudentClass(student_id=6, class_id=3, semester_id=1)
         #
         # # Thêm vào phiên làm việc và commit
         # db.session.add_all(
         #     [student_class1, student_class2, student_class3, student_class4, student_class5, student_class6])
         # db.session.commit()