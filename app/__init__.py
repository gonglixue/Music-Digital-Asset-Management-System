from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config

# 把程序实例的创建过程移到可显式调用的工厂函数中

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'  # 安全等级设为strong，Flask-Login 会记录客户端IP地址和浏览器的用户代理信息，如果发现异动就会登出用户
login_manager.login_view = 'auth.login'		 # 设置登录页面的端点，登录路由在auth蓝本中定义，因此要在前面加上蓝本的名字。

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	
	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	
	# 附加路由和自定义的错误页面
	
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint) # 蓝本在工厂函数中注册到函数上
	
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint,url_prefix='/auth') 
	# url_prefix是可选参数，注册后蓝本中定义的所有路由都会加上指定的前缀。
	# 例如auth蓝本中定义的/login路由会注册成/auth/login
	
	return app
