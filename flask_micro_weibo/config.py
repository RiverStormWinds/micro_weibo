import os

from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from sqlalchemy import create_engine

from flask import Flask

from flask_migrate import MigrateCommand, Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_script import Manager
# 直接创建一个完整的异常堆栈跟踪路径，如果没有flask_script Manager，则需要
# 手动输入export FLASK_DEBUG=1 制造环境变量，运行flask run命令进入异常堆栈跟踪界面，
# 使用Manager则省去了上文繁琐的环境变量及堆栈跟踪运行操作，比较方便
from flask import Blueprint


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'try it'
    # SECRET_KEY: flask扩展使用密钥值作为加密密钥，生成签名或令牌
    # Flask-WTF插件使用SECRET_KEY保护网页表单免受csrf恶意攻击
    SQLALCHEMY_DATABASE_URI = 'sqlite:////home/storm/PycharmProjects/flask_dog_book/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    engine = create_engine('sqlite:////home/storm/PycharmProjects/flask_dog_book/app.db', pool_pre_ping=True)

    # 分页显示
    POSTS_PER_PAGE = 3

    # 语言支持：
    LANGUAGES = ['en', 'zh']


def result_init():
    # 初始化app
    app = Flask(__name__)
    app.env = 'development'
    app.debug = True
    app.config.from_object(BaseConfig)  # 指定app是由Config类进行配置

    # 初始化蓝图
    user = Blueprint('user', __name__)

    # 初始化manager
    manager = Manager(app)

    # 初始化db
    db = SQLAlchemy(app)
    db.init_app(app)
    Migrate(app, db)
    manager.add_command('db', MigrateCommand)

    # 初始化login_Manager
    login = LoginManager(app)

    # 初始化flask-bootstrap
    bootstrap = Bootstrap(app)

    # 初始化时区信息
    moment = Moment(app)

    # 初始化国际化模块
    babel = Babel(app)

    return app, db, manager, user, login, bootstrap, moment, babel


result = result_init()
app = result[0]
db = result[1]
manager = result[2]
user = result[3]
login = result[4]
bootstrap = result[5]
moment = result[6]
babel = result[7]

