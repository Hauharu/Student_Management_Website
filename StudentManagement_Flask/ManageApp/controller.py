from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from ManageApp import dao
import hashlib  # Để mã hóa mật khẩu (nếu cần)

def index():
    return render_template('index.html')

def user_signin():
    if current_user.is_authenticated:  # Kiểm tra nếu đã đăng nhập
        return redirect(url_for('index.py'))  # Sử dụng 'index' thay vì 'index.html'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password = hashlib.md5(password.encode('utf-8')).hexdigest()  # Mã hóa mật khẩu

        # Lấy thông tin user từ database
        user = dao.auth_user(username=username,password=password)
        if user and user.password == password:  # So sánh mật khẩu
            login_user(user=user)  # Đăng nhập người dùng
            return redirect(url_for('index'))  # Chuyển về trang chủ

        flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')  # Hiển thị thông báo lỗi

    return render_template('login.html')  # Hiển thị giao diện đăng nhập