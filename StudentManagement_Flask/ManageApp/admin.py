import hashlib
from ManageApp import app, db, dao
from flask_login import current_user, logout_user
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from flask import redirect, request, url_for
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from wtforms.fields.numeric import IntegerField
from wtforms import validators
from ManageApp.models import UserRole, UserGender, StudentGrade, ScoreType, Regulations, SemesterType, SemesterType, \
    UserInformation, User, Subject, Teach, Class, Student, Regulation, Semester, Score, ScoreDetail


# Cấu hình cách hiển thị và tương tác với các mô hình trong giao diện quản trị.
class AuthenticatedModelView(ModelView):
    column_display_pk = True
    can_view_details = True
    edit_modal = True
    details_modal = True
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


# Người dùng đã xác thực có vai trò ADMIN mới có thể truy cập.
class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


# Dùng để soạn thảo văn bản
class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')

        return super().__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


# Trang chủ quản trị
class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', user_count = dao.user_count())


# Quản lý đăng xuất đưa ra trang đăng nhập
class LogoutView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')


# quay về trang chủ
class BackHomeView(BaseView):
    @expose('/')
    def __index__(self):
        return redirect(url_for('index'))


class StudentView(AuthenticatedModelView):
    column_searchable_list = ['fullName']
    column_filters = ['fullName', 'email', 'dateOfBirth']

    column_editable_list = ['fullName']
    column_export_list = ['students']
    column_labels = {
        'id': 'Mã số',
        'fullName': 'Họ và tên',
        'gender': 'Giới tính',
        'dateOfBirth': 'Ngày sinh',
        'address': 'Địa chỉ',
        'phoneNumber': 'Số điện thoại',
        'email': 'Email'

    }
    column_sortable_list = ['id', 'fullName']

    page_size = 20
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'address': CKTextAreaField
    }


class MyClassView(AuthenticatedModelView):
    column_sortable_list = ['className', 'quantity']

    column_labels = {
        'id': 'Mã lớp',
        'className': 'Tên lớp',
        'quantity': 'Sĩ số lớp',
        'grade': 'Khối',
        'students': 'hoc sinh'
    }


# Quản lý người dùng
class UserView(AuthenticatedModelView):
    column_exclude_list = ['username', 'password', 'user_role', 'active', 'user_information']
    column_labels = {
        'username': 'Tên đăng nhập',
        'password': 'Mật khẩu',
        'user_role': 'Vai trò',
        'active': 'Trạng thái',
        'user_information': 'Họ tên người dùng'
    }


class MySubjectView(AuthenticatedModelView):
    def __init__(self, model, session, **kwargs):
        super().__init__(model=model, session=session, **kwargs)  # Pass model and session to ModelView
        # Any additional initialization can go here

    column_list = ['id', 'subjectName', 'grade', 'exam_15mins', 'exam_45mins', 'exam_Final']
    column_searchable_list = ['id', 'subjectName']
    column_filters = ['id', 'subjectName', 'grade']
    column_labels = {
        'subjectName': 'Tên môn học',
        'grade': 'Khối',
        'exam_15mins': 'Số bài kiểm tra 15 phút',
        'exam_45mins': 'Số bài kiểm tra 45 phút',
        'exam_Final': 'Số Bài kiểm tra cuối kỳ'
    }
    form_extra_fields = {
        'exam_15mins': IntegerField('Số bài kiểm tra 15 phút', validators=[validators.NumberRange(min=1, max=5)]),
        'exam_45mins': IntegerField('Số bài kiểm tra 45 phút', validators=[validators.NumberRange(min=1, max=3)]),
        'exam_Final': IntegerField('Số Bài kiểm tra cuối kỳ', validators=[validators.NumberRange(min=1, max=1)])
    }


# Quản lý quy định
class MyRegulationView(AuthenticatedModelView):
    def __init__(self, model, session, **kwargs):
        super().__init__(model=model, session=session, **kwargs)  # Pass model and session to ModelView

    column_list = [
        'id', 'regulationName', 'content', 'min_value', 'max_value', 'created_date', 'updated_date'
    ]
    column_labels = {
        "regulationName": "Tên quy định",
        "content": "Nội dung",
        "min_value": "Độ tuổi tối thiểu",
        "max_value": "Độ tuổi tối đa",
        "created_date": "Ngày tạo",
        "updated_date": "Ngày cập nhật"
    }


def combined_data(counts_students_of_classes, stats_with_avg):
    combined_data = {}

    # Combine counts_students_of_classes into the combined_data dictionary
    for c in counts_students_of_classes:
        combined_data[c[0]] = (c[0], c[1], c[2], None)

    # Update combined_data with the counts from stats_with_avg
    for s in stats_with_avg:
        if s[0] in combined_data:
            combined_data[s[0]] = (
                s[0], combined_data[s[0]][1], combined_data[s[0]][2], s[2], (s[2] / combined_data[s[0]][2]) * 100)

    # Convert the combined_data dictionary to a list of tuples
    combined_data_list = list(combined_data.items())

    return combined_data_list


# Xem số liệu thống kê
class StatsView(BaseView):
    @expose('/')
    def index(self):
        subjects = dao.get_subjects()
        years = dao.get_years()
        counts_students_of_classes = dao.count_students_of_classes_by_subject_and_period(
            subject_id=request.args.get('subject_id'),
            semester=request.args.get('semester'),
            year=request.args.get('year'))
        stats_with_avg = dao.count_students_of_classes_by_subject_and_period(subject_id=request.args.get('subject_id'),
                                                                             semester=request.args.get('semester'),
                                                                             year=request.args.get('year'),
                                                                             avg_gt_or_equal_to=5)
        stats = combined_data(counts_students_of_classes=counts_students_of_classes, stats_with_avg=stats_with_avg)
        subject = dao.get_subject_by_id(subject_id=request.args.get('subject+id'))
        period = dao.get_period(semester=request.args.get('semester'), year=request.args.get('year'))
        return self.render('admin/stats.html', subjects=subjects, years=years,
                           stats=stats,
                           subject=subject, period=period)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


# Thiết lập quản trị
admin = Admin(app, index_view=HomeView(), name="Trang quản trị", template_mode='bootstrap4')
admin.add_view(BackHomeView(name='Trang chính'))
admin.add_view(UserView(User, db.session, name='User'))
admin.add_view(MyClassView(Class, db.session, name='Lớp', category='QL Lớp'))
admin.add_view(StudentView(Student, db.session, name='Học sinh', category="QL Điểm HS"))
admin.add_view(MySubjectView(Subject, db.session, name='Môn học', category="QL Điểm HS"))
admin.add_view(MyRegulationView(Regulation, db.session, name='Quản lý quy định'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
