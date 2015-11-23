from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Length, Email,Regexp,EqualTo
from flask_wtf.file import FileRequired,FileAllowed, FileField
from wtforms import ValidationError
from ..models import User,Category
from flask import request
#from flask.ext.login import current_user


class LoginForm(Form):
	email = StringField('邮箱地址',validators=[Required(),Length(1,64),Email()])
	password = PasswordField('密码',validators=[Required()])
	remember_me = BooleanField('记住登录状态') # 复选框 在浏览器中写入一个长期有效的cookie
	submit = SubmitField('登录')

class RegistrationForm(Form):
	email = StringField('用于登录的邮箱地址',validators=[Required(),Length(1,64),Email()])
	username = StringField('用户昵称',validators=[\
		Required(),Length(1,64),Regexp('[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters,numbers,dots or underscores')])
	password = PasswordField('密码',validators=[\
		Required(),EqualTo('password2',message='Passwords must match.')])
	password2 = PasswordField('确认密码',validators=[Required()])
	submit = SubmitField('注册')
	
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')
			
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')
			
class FileForm(Form):
	image = FileField('Albumn Cover',validators=[FileRequired(),FileAllowed(['jpg','png'],'Images only!')])
	mp3 = FileField('Mp3 File',validators=[FileRequired(),FileAllowed(['mp3'],'Mp3 only!')])
	songname = StringField('name',validators=[Required()])
	singer = StringField('singer',validators=[Required()])
	classname = SelectField('classification',choices=[('popular','popular'),('violin','violin'),('folkmusic','folkmusic'),('lovesongs','lovesongs'),('rock','rock'),('electronic','electronic'),('Japanese','Japanese'),('gufeng','古风'),('yueyu','粤语')])
	#classname = SelectField('classification')
	description = StringField('description')
	submit = SubmitField('Upload')
	
	# def init(self):
		# form = FileForm()
		# list = Category.query.all()
		# count = Category.query.count()
		# tupleList = []
		# for i in range(0,count):
			# tupleList.append((list[i].name,list[i].name))
		
		# form.classname.choices=tupleList

class UserNameForm(Form):
	username = StringField('新昵称：',validators=[Required()])
	submit = SubmitField('更改昵称')	
	
class SongInfoForm(Form):
	songname = StringField('歌曲名：',validators=[Required()])
	singer = StringField('歌手名：',validators=[Required()])
	description = StringField('简介：')
	submit = SubmitField('确认修改')

		
