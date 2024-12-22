from ManageApp import app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from ManageApp import app, db, login , utils

admin = Admin(app=app, name='Quản trị Trường THPT',
              template_mode='bootstrap4',
)
# admin.add_view(ModelView(User, db.session,
#                         name='Tài khoản',
#                         menu_icon_type='fa',
#                         menu_icon_value='fa-users'))
# # Staff
# admin.add_view(ModelView(Student, db.session,
#                           name='Học sinh',
#                           category="Cá nhân",
#                           menu_icon_type='fa',
#                           menu_icon_value='fa-graduation-cap'))
# # Staff
# # admin.add_view(Change_class(Student, db.session,
# #                             name='Điều chỉnh lớp học',
# #                             category="Lớp học"))
# # Admin
#
# admin.add_view(ModelView(Teacher, db.session,
#                            name='Giáo viên',
#                            category="Cá nhân",
#                            menu_icon_type='fa',
#                            menu_icon_value='fa-podcast'))
# # Admin
# admin.add_view(ModelView(SchoolStaff, db.session,
#                           name='Nhân viên',
#                           category="Cá nhân",
#                           menu_icon_type='fa',
#                           menu_icon_value='fa-briefcase'))
#