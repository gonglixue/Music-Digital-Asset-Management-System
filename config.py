import os
basedir = os.path.abspath(os.path.dirname(__file__))

# 本文件设定了程序的多项配置。开发、测试、生产环境使用不同的数据库

# Config基类 通用配置
class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string' 
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
	FLASKY_MAIL_SENDER = 'Flasky Admin<951228glx@sina.com>'
	FLASKY_ADMIN = os.environ.get('FLASK_ADMIN')
	FLASKY_COMMENTS_PER_PAGE = 10
	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.sina.com'
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # 导入环境变量，先在cmd里设置环境变量, eg： set MAIL_USERNAME = 951228glx@sina.com
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')
	
class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir,'data-test.sqlite')
		
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
		'sqlite:///' + os.path.join(basedir,'data.sqlite')
	
config = {
	'development':DevelopmentConfig,
	'testing':TestingConfig,
	'production':ProductionConfig,
	
	'default':DevelopmentConfig
}
