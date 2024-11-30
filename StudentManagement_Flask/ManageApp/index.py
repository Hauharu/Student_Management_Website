from ManageApp import app
from flask import render_template, request, redirect, url_for


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method.__eq__('POST'):
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '123':
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route("/admin")
def admin():
    return  render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)
