import enum
import hashlib
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date, Enum, DateTime, CheckConstraint, \
    UniqueConstraint
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from flask_login import UserMixin
from ManageApp import db, app


####################################### Class Abstract ##########################################

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


########################################## Class Enums ###########################################

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


############################################### Classes ##########################################

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

    student = relationship('Student', backref='student_info', uselist=False, lazy=True)
    admin = relationship('Admin', backref='admin_info', uselist=False, lazy=True)
    teacher = relationship('Teacher', backref='teacher_info', uselist=False, lazy=True)
    staff = relationship('Staff', backref='staff_info', uselist=False, lazy=True)

    def __str__(self):
        return self.username


class Teacher(BaseModel):
    __tablename__ = 'teacher'
    qualification = Column(String(20))
    user = relationship("User", backref="teacher", lazy=True, uselist=False)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)
    classes = relationship("Class", backref="teacher", lazy=True)
    subject = relationship("TeacherSubject", backref="teacher", lazy=True)


class Staff(BaseModel):
    __tablename__ = 'staff'
    user = relationship("User", backref="staff", lazy=True, uselist=False)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)


class Admin(BaseModel):
    __tablename__ = 'admin'
    user = relationship("User", backref="admin", lazy=True, uselist=False)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)


class Semester(BaseModel):
    __tablename__ = 'semester'
    semesterName = Column(String(50), nullable=False)
    year = Column(Integer, default=datetime.now().year)
    student = relationship("Student", backref="semester", lazy=True)
    score = relationship("Score", backref="semester", lazy=True)
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
    teachers = relationship("TeacherSubject", backref="subject_detail", lazy=True)


class TeacherSubject(BaseModel):
    __tablename__ = 'teacher_subject'
    teacher_id = Column(Integer, ForeignKey(Teacher.user_id), nullable=False)
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
    teacher_id = Column(Integer, ForeignKey(Teacher.id), unique=True)
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
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)

    classes = relationship('Class', backref='teach', lazy=True)
    semester = relationship('Semester', backref='teach', lazy=True)
    subject = relationship('Subject', backref='teach', lazy=True)
    teacher = relationship('User', backref='teach', lazy=True)

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


if __name__ == "__main__":
    from ManageApp import app

    with app.app_context():
        # db.drop_all()
        db.create_all()
    #
    # import  hashlib
    # tkadm = TaiKhoan(username='admin', password=str(hashlib.md5('admin123'.encode('utf-8')).hexdigest()), loaiTaiKhoan=VaiTroTaiKhoan.ADMIN)
    # tkgv = TaiKhoan(username='giaovien', password=str(hashlib.md5('giaovien123'.encode('utf-8')).hexdigest()), loaiTaiKhoan=VaiTroTaiKhoan.TEACHER)
    # tknv = TaiKhoan(username='nhanvien', password=str(hashlib.md5('nhanvien123'.encode('utf-8')).hexdigest()), loaiTaiKhoan=VaiTroTaiKhoan.STAFF)
    #
    # db.session.add(tkadm)
    # db.session.add(tkgv)
    # db.session.add(tknv)
    #
    # gv1 = GiaoVien(hoTen='Nguyễn Văn A', ngaySinh='2000-10-01', gioiTinh='Nam', email='example@gmail.com', diaChi='Hồ Chí Minh', soDT='0123456789', taiKhoan_id=2)
    # db.session.add(gv1)
    #
    # nv1 = NhanVien(hoTen='Nguyễn Hoài Tâm', ngaySinh='2003-08-16', email='2151053055tam@ou.edu.vn', soDT='0394873588', taiKhoan_id=3)
    # db.session.add(nv1)
    #
    # k10 = KhoiLop(tenKhoi='Khối 10')
    # k11 = KhoiLop(tenKhoi='Khối 11')
    # k12 = KhoiLop(tenKhoi='Khối 12')
    # db.session.add_all([k10, k11, k12])

    # l10a1 = Lop(tenLop='10A1', siSo=40, khoiLop_id=1)
    # l11a1 = Lop(tenLop='11A1', siSo=39, khoiLop_id=2)
    # l12a1 = Lop(tenLop='12A1', siSo=35, khoiLop_id=3)
    # db.session.add_all([l10a1, l11a1, l12a1])
    #
    # hs1 = HocSinh(hoTen='Nguyễn Học Sinh', ngaySinh='2003-12-26', gioiTinh='Nam', diaChi='Hồ Chí Minh', soDT='012395784', email='sinh@ou.edu.vn', ngayNhapHoc='2022-05-02', lop_id=1)
    # db.session.add(hs1)
    #
    # namhoc = NamHoc(tenNam='NH2425')
    # db.session.add(namhoc)

    # hk12425 = HocKy(tenHocKy='HK1_2425', ngayBD='2024-01-01', ngayKT='2024-05-21', namHoc_id=2)
    # db.session.add(hk12425)
    #
    # mhtoan = MonHoc(tenMon='Toán 10')
    # db.session.add(mhtoan)
    #
    # d1 = Diem(tenDiem='Điểm 15p', monHoc_id=1, hocSinh_id=1, hocKy_id=2)
    # db.session.add(d1)
    #
    # ld15p = LoaiDiem(tenLoaiDiem='15 phút')
    # ld1t = LoaiDiem(tenLoaiDiem='1 tiết')
    # ldck = LoaiDiem(tenLoaiDiem='Cuối kỳ')
    # db.session.add_all([ld15p, ld1t, ldck])
    #
    # ctd1 = ChiTietDiem(diem=10, loaiDiem_id=1, diem_id=2)
    # db.session.add(ctd1)
    #
    # qd = QuyDinh(tuoiToiThieu=15, tuoiToiDa=20, siSoToiDa=40)
    # db.session.add(qd)
    #
    # lgv = LopGiaoVien(lop_id=1, giaoVien_id=1)
    # db.session.add(lgv)
    #
    # mhgv = MonHocGiaoVien(monHoc_id=1, giaoVien_id=1)
    # db.session.add(mhgv)

    # db.session.commit()
