from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db
from . import login_manager
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True) # id 在会话提交后会自动生成
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64),unique=True,index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	password_hash=db.Column(db.String(128))
	# 后续可能还要添加：最近听过的歌曲记录、收藏夹
	list = db.Column(db.Text,default='')
	comments = db.relationship('Comment',backref='author',lazy='dynamic')
	
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')
	
	@password.setter
	# def passwrod(self,password):
		# self.password_hash = generate_password_hash(password)
		
	# def verify_password(self,password):
		# return check_password_hash(self.password_hash,password)
		
	def password(self,password):
		self.password_hash = password	
	def verify_password(self,password):
		return self.password_hash==password

	def __repr__(self):
		return '<User %r>' % self.username
		
class Song(db.Model):
	__tablename__='songs'
	songname = db.Column(db.String(64),index=True)
	songid = db.Column(db.String(64),index=True)
	songclass = db.Column(db.String(64),index=True)
	singer = db.Column(db.String(64),index=True)
	id = db.Column(db.Integer,primary_key=True)
	comments = db.relationship('Comment',backref='song',lazy='dynamic')
	
#从song到comment有一对多的关系，从user到comment有一对多关系
class Comment(db.Model):
	__tablename__='comments'
	id = db.Column(db.Integer,primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	song_id = db.Column(db.Integer,db.ForeignKey('songs.id'))
	disabled = db.Column(db.Boolean)
	
class Category(db.Model):
	__tablename__='category'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True, index=True)
	count = db.Column(db.Integer)
	
		
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id)) #该回调函数返回用户对象
