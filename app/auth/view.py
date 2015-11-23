from flask import render_template,redirect,request,url_for,flash,session
from flask.ext.login import login_user, logout_user, login_required,current_user
from . import auth
from ..models import User,Category,Song,Comment # 上一层的models
from .. import db
from .forms import LoginForm,RegistrationForm,FileForm,UserNameForm,SongInfoForm
from ..email import send_email
from werkzeug import secure_filename
import os
from PIL import Image
from PIL import ImageEnhance
from . import watermark
from sqlalchemy import desc

@auth.route('/login/',methods=['GET','POST'])
def login():
	form = LoginForm()
	#session['current_name'] = ''
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)  # 调用Flask-Login 中的login_user()函数，在用户会话中把用户标记为已登录
			session['current_name'] = user.username
			session['pay']=0
			if user.role_id == 1:
				return redirect(request.args.get('next') or url_for('auth.admin'))
			else:
				return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password.')
	return render_template('auth/login.html',form=form)
	
@auth.route('/logout/')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))
	
@auth.route('/register/',methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email = form.email.data,username=form.username.data,password=form.password.data,role_id=2,money=20) # 管理员role_id = 1
		db.session.add(user)
		flash('You can now login.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html',form=form)
	
@auth.route('/admin/',methods=['GET','POST'])
@login_required
def admin():
	form = FileForm()
	#form.init()
	TEMP_FOLDER = 'app/static/temp'
	#classname = 'popular'
	#UPLOAD_FOLDER = 'app/static/'+classname+'/'
	if form.validate_on_submit():
		file_image_name = secure_filename(form.image.data.filename) # 图片文件
		classname = form.classname.data # 分类名
		#category = Category.query.filter_by(name=classname)
		songname = form.songname.data # 歌曲名
		singer = form.singer.data # 歌手
		description = form.description.data # 描述
		
		UPLOAD_FOLDER = 'app/static/'+classname+'/'		
		f = request.files['image'] # 引号里的image是表单域名
		f_mp3 = request.files['mp3']
		f.save(os.path.join(TEMP_FOLDER,file_image_name))	#用户上传的文件先保存在服务器temp文件夹下
		img = Image.open(os.path.join(TEMP_FOLDER,file_image_name))	#从文件夹中取出进行格式转换，再保存到相应的分类文件夹下
		category = Category.query.filter_by(name=classname).first()
		num = category.count + 1
		if num<10:
			img.save(UPLOAD_FOLDER+"00%r"%num+".PNG","PNG")
			new_image_s_filename = os.path.join(UPLOAD_FOLDER,'00%r.PNG'%num)
			f_mp3.save(os.path.join(UPLOAD_FOLDER,"00%r.mp3"%num))
		else:
			img.save(UPLOAD_FOLDER+"0%r"%num+".PNG","PNG")
			new_image_s_filename = os.path.join(UPLOAD_FOLDER,'0%r.PNG'%num)
			f_mp3.save(os.path.join(UPLOAD_FOLDER,"0%r.mp3"%num))
		category.count = category.count + 1	#每上传一个新的资源，该分类的count加一
		
		newsong = Song(songname=songname,songclass=classname,singer=singer,songid=num,category=category,description=description,times=0,score=0) #每上传一个资源，新建一个Song对象插入数据库
		
		db.session.add(category)
		db.session.add(newsong)
		db.session.commit()
		
		#裁剪
		clipim = Image.open(new_image_s_filename)
		dst_h = 2
		dst_w = 5
		ori_w,ori_h = clipim.size
		dst_scale = float(dst_w)/dst_h
		ori_scale = float(ori_w)/ori_h
		if ori_scale<=dst_scale:
			width = ori_w
			height = int(width/dst_scale)
			x=0
			y=(ori_h-height)/2
		else:
			height = ori_h
			width = int(height*dst_scale)
			x = (ori_w - width)/2
			y = 0
		box = (int(x),int(y),int(width+x),int(height+y))
		newIm = clipim.crop(box)
		newIm.save(new_image_s_filename,"PNG")
		
		
		#new_image_s_filename = os.path.join(UPLOAD_FOLDER,'logo.PNG')
		# 加水印
		MARKIMAGE = os.path.join('app/static','logo.PNG')
		POSITION = ('LEFTTOP','RIGHTTOP','CENTER','LEFTBOTTOM','RIGHTBOTTOM',"title","scale")
		watermark.water_mark(new_image_s_filename,MARKIMAGE,POSITION[2],opacity=0.5).save(new_image_s_filename,quality=90)
		
		
		flash('Upload Successfully!')
		return redirect(url_for('auth.admin'))
	return render_template('auth/admin.html',form=form)

@auth.route('/admin/alluser/',methods=['GET','POST'])
@login_required
def search_alluser():
	count = User.query.count()
	userlist = User.query.all()
	return render_template('auth/allusers.html',count=count, userlist=userlist)
	
@auth.route('/admin/allsong/',methods=['GET','POST'])
@login_required
def search_allsong():
	count = Song.query.count()
	songlist = Song.query.all()
	return render_template('auth/allsongs.html',count=count, songlist=songlist)
	
# @auth.route('/test/')
# def test():
	#return session['current_name']
	
@auth.route('/moderate/enable/<int:id>/')
@login_required
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.diabled = False
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('main.singlesong',songid=comment.song_id))
	
@auth.route('/moderate/disable/<int:id>/')
@login_required
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('main.singlesong',songid=comment.song_id))
	
@auth.route('/moderateSong/enable/<int:id>/')
@login_required
def song_enable(id):
	song = Song.query.get_or_404(id)
	song.disabled = False
	db.session.add(song)
	db.session.commit()
	return redirect(url_for('auth.search_allsong'))
	
@auth.route('/moderateSong/disable/<int:id>/')
@login_required
def song_disable(id):
	song = Song.query.get_or_404(id)
	song.disabled = True
	db.session.add(song)
	db.session.commit()
	return redirect(url_for('auth.search_allsong'))
	
		

	
@auth.route('/personalCenter/',methods=['GET','POST'])
@login_required
def person():
	form = UserNameForm()
	id = current_user.id
	user = User.query.get_or_404(id)
	if form.validate_on_submit():
		newname = form.username.data
		user.username = newname
		db.session.add(user)
		db.session.commit()
		flash('更改昵称成功!')
		return redirect(url_for('auth.person'))
	songlist = current_user.collection_songs
	collectNum = songlist.count()
	
	#热门
	hotList = db.session.query(Song).order_by(desc(Song.times))
	hotCount = db.session.query(Song).order_by(desc(Song.times)).count()
	if(hotCount>4):
		hotCount=4
	
	return render_template('auth/personal.html',form=form,songlist=songlist,collectNum=collectNum,hotList=hotList,hotCount=hotCount,user=user)
	
@auth.route('/personalCenter/cancelCollect/<int:id>/')
@login_required
def cancelCollect(id):
	song = Song.query.get_or_404(id)
	current_user.collection_songs.remove(song)
	db.session.add(current_user)
	db.session.commit()
	flash('已取消收藏')
	return redirect(url_for('auth.person'))
	
@auth.route('/SongInfo/<int:id>/',methods=['GET','POST'])
@login_required
def SongInfo(id):
	song = Song.query.get_or_404(id)
	form = SongInfoForm()
	if form.validate_on_submit():
		song.songname=form.songname.data
		song.singer = form.singer.data
		song.description = form.description.data
		db.session.add(song)
		db.session.commit()
		flash('修改成功')
		return redirect(url_for('auth.SongInfo',id=id))
	return render_template('auth/SongInfo.html/',song=song,form=form)
	
