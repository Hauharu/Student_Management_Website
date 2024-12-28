import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
from flask_babelex import Babel
from flask_mail import Mail


app = Flask(__name__)


app.secret_key = '@#$%^&*(#@#$%^&@#$%^&*@#$&%$@##$^!@#$%^&)(*&^%$#@!$%^'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/manage_db?charset=utf8mb4" % quote('12345678@')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["CN_PAGE_SIZE"] = 6


app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "hfh@gmail.ocm"
app.config['MAIL_PASSWORD'] ="hau uah ahu"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


cloudinary.config(
    cloud_name='dwwfgtxv4',
    api_key='847843234855491',
    api_secret='OEbZdz4wwMCsG_CEfXW6ScQFliI'
)


db = SQLAlchemy(app=app)
login = LoginManager(app=app)
babel = Babel(app=app)
mail = Mail(app)


@babel.localeselector
def get_locale():
    return 'vi'