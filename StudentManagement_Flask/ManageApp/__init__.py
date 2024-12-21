from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/manage_db?charset=utf8mb4" % quote('12345678@')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

login = LoginManager(app=app)

cloudinary.config(cloud_name='dwwfgtxv4',
                  api_key='847843234855491',
                  api_secret='OEbZdz4wwMCsG_CEfXW6ScQFliI')
