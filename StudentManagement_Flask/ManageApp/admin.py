from ManageApp import app, db, dao
from flask_login import current_user, logout_user
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, request, url_for
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from wtforms.fields.numeric import IntegerField
from wtforms import validators
from ManageApp.models import *


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
class AuthenticatedAdmin(BaseView):
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
        if not current_user.is_authenticated:
            return redirect(url_for('user_login'))

        if current_user.user_role != UserRole.ADMIN:
            return redirect(url_for('access_denied'))

        semester = request.args.get('semester', SemesterType.SEMESTER_1.name)
        year = request.args.get('year', datetime.now().year)

        # Gọi hàm để lấy thống kê học sinh theo học kỳ và năm học
        amount_of_students_by_period = dao.stats_amount_of_students_by_period(
            semester=semester,
            year=year
        )

        # Gọi hàm để lấy thống kê số lượng người dùng theo vai trò
        user_count = dao.user_count()

        # Trả về giao diện cùng dữ liệu cần thiết
        return self.render(
            'admin/index.html',
            user_count=user_count,
            amount_of_students_by_period=amount_of_students_by_period
        )

    def is_accessible(self):
        return True


# Quản lý đăng xuất đưa ra trang đăng nhập
class LogoutView(AuthenticatedAdmin):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')


# quay về trang chủ
class BackHomeView(BaseView):
    @expose('/')
    def __index__(self):
        return redirect(url_for('index'))


# Xem thông tin học sinh
class StudentView(AuthenticatedModelView):
    column_searchable_list = ['name']
    column_filters = ['name', 'email', 'dateOfBirth']
    column_list = ['id', 'name', 'gender', 'dateOfBirth', 'address', 'phoneNumber', 'email', 'grade']
    column_editable_list = ['name']
    column_export_list = ['students']
    can_edit = False
    can_delete = False
    column_labels = {
        'id': 'ID',
        'name': 'Họ và tên',
        'gender': 'Giới tính',
        'dateOfBirth': 'Ngày sinh',
        'address': 'Địa chỉ',
        'phoneNumber': 'Số điện thoại',
        'email': 'Email',
        'grade': 'Khối'

    }
    column_sortable_list = ['id', 'name']

    page_size = 20
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'address': CKTextAreaField
    }


# Hồ sơ người dùng
class UserInformationView(AuthenticatedModelView):
    can_export = False
    column_list = ['name', 'gender', 'dateOfBirth', 'address', 'phoneNumber', 'email', 'joined_date']
    column_labels = {
        'name': 'Họ và tên',
        'gender': 'Giới tính',
        'dateOfBirth': 'Ngày sinh',
        'address': 'Địa chỉ',
        'phoneNumber': 'Số điện thoại',
        'email': 'Email',
        'joined_date': 'Ngày tham gia'
    }
    column_filters = [
        'name',
        'email',
        'phoneNumber',
    ]
    can_view_details = True


# Quản lý người dùng
class UserView(AuthenticatedModelView):
    column_list = ['id', 'username', 'userInformation', 'user_role', 'is_active']
    can_export = False
    can_edit = False
    column_filters = [
        'username',
        'user_role',
    ]
    form_excluded_columns = ['classes']
    column_labels = {
        'id': 'ID',
        'username': 'Tên đăng nhập',
        'userInformation': "Họ và tên",
        'user_role': 'Vai trò',
        'is_active': 'Trạng thái'
    }

# Quản l môn học
class SubjectView(AuthenticatedModelView):
    column_list = ['id', 'subjectName', 'grade', 'exam_15mins', 'exam_45mins', 'exam_Final']
    column_searchable_list = ['subjectName']
    column_filters = [
        'subjectName',
        'grade',
        'exam_15mins',
        'exam_45mins',
    ]
    form_excluded_columns = ['teach']
    column_labels = {
        'id': 'ID',
        'subjectName': 'Tên môn học',
        'grade': 'Khối',
        'exam_15mins': 'Số bài 15 phút',
        'exam_45mins': 'Số bài 45 phút',
        'exam_Final': 'Bài cuối kỳ',
    }
    form_extra_fields = {
        'exam_15mins': IntegerField('Số bài kiểm tra 15 phút', validators=[validators.NumberRange(min=1, max=5)]),
        'exam_45mins': IntegerField('Số bài kiểm tra 45 phút', validators=[validators.NumberRange(min=1, max=3)]),
        'exam_Final': IntegerField('Số Bài kiểm tra cuối kỳ', validators=[validators.NumberRange(min=1, max=1)])
    }

    def apply(view, context, model, name):
        if model.teachs:
            result = []
            for teaching in model.teachs:
                # Lấy thông tin từ các quan hệ liên kết
                class_name = teaching.classes.className if teaching.classes else None
                semester_name = teaching.semester.semester if teaching.semester else None
                teacher_name = teaching.teacher.UserInformation.name if teaching.teacher and teaching.teacher.UserInformation else None

                result.append(f'Lớp: {class_name}, {semester_name}, Giảng viên: {teacher_name}')
            return ', '.join(result)
        return 'Rỗng'

    column_formatters = {
        'teachs': apply
    }


# Quản lý quy định
class RegulationView(AuthenticatedModelView):
    column_list = [
        'id', 'regulationName', 'content', 'min_value', 'max_value', 'classes'
    ]
    column_searchable_list = ['regulationName']
    can_edit = True
    can_export = False
    form_excluded_columns = ['students']

    column_labels = {
        'id': 'ID',
        "regulationName": "Tên quy định",
        "content": "Nội dung",
        "min_value": "Giá trị tối thiểu",
        "max_value": "Giá trị tối đa",
        'classes': 'Lớp'
    }

# thống kê
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

# Quản lý thống kê
class StatsView(BaseView):
    @expose('/')
    def index(self):
        subjects = dao.get_subjects()
        years = dao.get_years()
        current_year = dao.get_current_year()
        counts_students_of_classes = dao.count_students_of_classes_by_subject_and_period(
            subject_id=request.args.get('subjectId'),
            semester=request.args.get('semester'),
            year=request.args.get('year'))
        stats_with_avg = dao.count_students_of_classes_by_subject_and_period(subject_id=request.args.get('subjectId'),
                                                                             semester=request.args.get('semester'),
                                                                             year=request.args.get('year'),
                                                                             avg_gt_or_equal_to=5)
        stats = combined_data(counts_students_of_classes=counts_students_of_classes, stats_with_avg=stats_with_avg)
        subject = dao.get_subject_by_id(subject_id=request.args.get('subjectId'))
        period = dao.get_period(semester=request.args.get('semester'), year=request.args.get('year'))
        return self.render('admin/stats.html', subjects=subjects, years=years,
                           stats=stats,
                           subject=subject, period=period)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


# Thiết lập quản trị
admin = Admin(app, index_view=HomeView(), name="Trang quản trị", template_mode='bootstrap4')
admin.add_view(BackHomeView(name='Trang chính'))
admin.add_view(UserInformationView(UserInformation, db.session, name='Hồ sơ người dùng'))
admin.add_view(StudentView(Student, db.session, name='Hồ sơ học sinh'))
admin.add_view(UserView(User, db.session, name='Quản lý người dùng'))
admin.add_view(RegulationView(Regulation, db.session, name='Quản lý quy định'))
admin.add_view(SubjectView(Subject, db.session, name='Quản lý Môn học'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
