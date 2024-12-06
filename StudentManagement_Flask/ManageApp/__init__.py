from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/table_test?charset=utf8mb4" % quote('12345678@')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)


