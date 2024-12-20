import hashlib
from ManageApp.models import User  # Import model User
from ManageApp import app, db    # SQLAlchemy session

def get_user_by_username(username):
    return User.query.filter(User.username == username).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()

def auth_user(username, password, role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(role)).first()
