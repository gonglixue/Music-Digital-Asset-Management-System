from flask import render_template, session, redirect, url_for, current_app, request,flash,send_from_directory
from .. import db
from ..models import User,Comment,Song,Category
from ..email import send_email
from . import main
from .forms import NameForm,CommentForm
from flask.ext.login import login_user, logout_user, login_required,current_user
from datetime import datetime
import random
import os
import urllib
import urllib.request
from bs4 import BeautifulSoup
from sqlalchemy import desc, or_, func


@main.route('/', methods=['GET', 'POST'])
def index():
	list = Category.query.all()   #保存所有分类
	numClass = Category.query.count()  #记录总共有多少个分类
	randomList={}
	songidList={}
	for i in range(0,numClass):  #为每个分类生成一个随机数，该数要小于该类的歌曲总数
		if list[i].count>0:   #如果该分类有歌  （如果该分类有歌但所有歌都下架了怎么办？_(:з」∠)_
			while(True):
				randomList[i]=random.randint(1,list[i].count)
				song=Song.query.filter_by(songid=randomList[i]).first()
				if(song.disabled==False):  #若随机抽到的歌曲没有下架，那么跳出while
					break
			songidList[i]=song.id
		else:
			randomList[i] = 0
	return render_template('index.html',numClass=numClass,list=list,randomList=randomList,songidList=songidList)
	
@main.route('/search/result/',methods=['GET','POST'])
def search():
	word = request.form['keyword']
	session['word'] = word
	resultList = Song.query.filter(or_(Song.songname.ilike('%'+session['word']+'%'),Song.singer==session['word'],Song.songclass==session['word']))
	count = resultList.count()
	return render_template('searchResult.html',songlist = resultList,count=count)

@main.route('/search/<string:word>/')
def search2(word):
	session['word']=word
	resultList = Song.query.filter(or_(Song.songname==session['word'],Song.singer==session['word'],Song.songclass==session['word']))
	count = resultList.count()
	session['word']=word
	return render_template('searchResult.html',songlist = resultList,count=count)
	
@main.route('/search/song/',methods=['GET','POST'])
def search_song():
	#word = request.form['keyword']
	word=session['word']
	#多条件查询
	resultList = Song.query.filter_by(songname=word)
	count = resultList.count()
	return render_template('searchResult.html',songlist = resultList,count=count)
	
@main.route('/search/singer/',methods=['GET','POST'])
def search_singer():
	word = session['word']
	resultList = Song.query.filter_by(singer=word)
	count = resultList.count()
	return render_template('searchResult.html',songlist = resultList,count=count)
	
@main.route('/search/class/',methods=['GET','POST'])
def search_class():
	word = session['word']
	resultList = Song.query.filter_by(songclass=word)
	count = resultList.count()
	return render_template('searchResult.html',songlist = resultList,count=count)
	
@main.route('/song/<int:songid>/',methods=['GET','POST'])
def singlesong(songid):
	form = CommentForm();
	if form.validate_on_submit():
		comment = Comment(song_id=songid,author_id=current_user.id,body=form.body.data,disabled=False)
		db.session.add(comment)
		#评论后用户积分+1
		current_user.money = current_user.money + 1
		db.session.add(current_user)
		db.session.commit()
		flash('评论成功！获得1个积分，您已有%r积分'%current_user.money)
		return redirect(url_for('main.singlesong',songid=songid))
		form.body.data=''
		
	song = Song.query.filter_by(id=songid).first()
	classification = Category.query.filter_by(name=song.songclass).first()
	if(classification.pay==True):
		if(current_user.is_authenticated):
			if(session.get('pay')!=1):
				if(current_user.money<3):
					return "<script>alert('收听本分类歌曲需扣除3个积分！积分不足/(ㄒoㄒ)/~~')</script>"
				else:
					current_user.money=current_user.money-3
					db.session.add(current_user)
					db.session.commit()
					flash('扣除3个积分:D 其实这是个bug，因为会重复扣除积分。。')
					session['pay']=1
		else:
			return "<script>alert('该分类歌曲需要扣除积分，请先登录:D')</script>"
	#testtimes = Song.query.filter_by(times>0).first()
	if(song):
		classname = song.songclass
		song.times = song.times+1 #收听次数+1
		
	else:
		return render_template('404.html')  #歌曲id不存在
	count = Comment.query.filter_by(song_id=songid).count()
	commentlist = Comment.query.filter_by(song_id=songid)
	
	#从豆瓣抓取相关音乐
	singer_test=song.singer
	url = "http://music.douban.com/subject_search?search_text="+urllib.parse.quote(singer_test)+"&cat=1003"
	page = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(page)
	title = list(range(5))
	link = list(range(5))
	image = list(range(5))
	article = soup.find(class_='article')
	table = article.find_all('table')
	i = 0
	for item in table:
		tag = item.find(class_='nbg')
		title[i] = tag['title']
		link[i] = tag['href']
		img_tag = tag.img
		image[i] = img_tag['src']
		i=i+1
		if(i==5):
			break
	
	return render_template('singlesong.html',form=form,commentlist=commentlist,count=count,classname=classname,songid=song.songid,song=song,title=title,link=link,image=image)
	#注意区分song的唯一id和在当前分类中的id
		
@main.route('/test/')
def test():
	return current_user.username
	
@main.route('/<string:classname>/')
def classification(classname):
	folder = 'app/static/'+classname+'/'
	classification = Category.query.filter_by(name=classname).first()
	if(classification.pay==True):
		if(session.get('pay')!= 1):
			if(current_user.money<3):
				return "<script>alert('对不起您的积分不足')</script>"
			else:
				current_user.money = current_user.money-3
				flash('您的积分已-3')
				session['pay'] = 1 #当前登录标记为已付费 _(:з」∠)_但是下次登录还是要付费的
	numSongs = classification.count
	songList = classification.songs
	#path = os.path.join('app',classification.name)
	#推荐热门音乐
	hotList = db.session.query(Song).order_by(desc(Song.times))
	hotCount = db.session.query(Song).order_by(desc(Song.times)).count()
	if(hotCount > 4):   #最多显示5首热门歌曲
		hotCount = 4
	return render_template('classification.html',numSongs=numSongs,songList=songList,classname=classname,hotList=hotList,hotCount=hotCount)
	
@main.route('/singer/')
def singer():
	singerList = db.session.query(Song.singer,func.count(Song.songname)).group_by(Song.singer).all()
	count = len(singerList)
	
	# i = 0;
	# title1 = list(range(count))
	# title2 = list(range(count))
	# title3 = list(range(count))
	# title4 = list(range(count))
	# info1 = list(range(count))
	# info2 = list(range(count))
	# info3 = list(range(count))
	# info4 = list(range(count))
	# for item in singerList:
		# url = "http://music.douban.com/subject_search?search_text="+urllib.parse.quote(item[0])+"&cat=1003"
		# page = urllib.request.urlopen(url).read()
		# soup = BeautifulSoup(page)
		# tag_a = soup.find(class_='musicial_title')
		# link = tag_a.get('href')
		# url = link
		# page = urllib.request.urlopen(url).read()
		# soup = BeautifulSoup(page)
		# tag = soup.find(class_='info')
		# ul = tag.find_all('li')
		# j = 0
		# for li in ul:
	
	#推荐热门音乐
	hotList = db.session.query(Song).order_by(desc(Song.times))
	hotCount = db.session.query(Song).order_by(desc(Song.times)).count()
	if(hotCount > 4):   #最多显示5首热门歌曲
		hotCount = 4
	return render_template('singer.html',singerList=singerList,count=count,hotList=hotList,hotCount=hotCount)
	
@main.route('/song/good/<int:id>/')
@login_required
def good(id):
	song = Song.query.get_or_404(id)
	song.score = song.score+1
	db.session.add(song)
	#点赞后把该歌曲添加到zan_songs里标记该用户已赞
	current_user.zan_songs.append(song)
	db.session.add(current_user)
	db.session.commit()
	return redirect(url_for('main.singlesong',songid=id))
	
@main.route('/song/cancelGood/<int:id>/')
@login_required
def cancelGood(id):
	song = Song.query.get_or_404(id)
	song.score = song.score-1
	db.session.add(song)
	#取消赞后把歌曲从zan_songs里移除
	current_user.zan_songs.remove(song)
	db.session.add(current_user)
	db.session.commit()
	return redirect(url_for('main.singlesong',songid=id))
	
@main.route('/dtest/')
def ttest():
	return "<script>alert('warning')</script>"
	#return render_template('test.html')
	
@main.route('/collect/<int:id>/<string:classname>/')
@login_required
def collect(id,classname):
	song = Song.query.get_or_404(id)
	current_user.collection_songs.append(song)
	db.session.add(current_user)
	db.session.commit()
	flash('收藏成功，可在个人中心查看所有收藏歌曲')
	return redirect(url_for('main.classification',classname=classname))
	
@main.route('/cancelcollect/<int:id>/<string:classname>/')
@login_required
def cancelCollect(id,classname):
	song = Song.query.get_or_404(id)
	current_user.collection_songs.remove(song)
	db.session.add(current_user)
	db.session.commit()
	flash('已取消收藏')
	return redirect(url_for('main.classification',classname=classname))
	
@main.route('/single/collect/<int:id>/')
@login_required
def singleCollect(id):
	song = Song.query.get_or_404(id)
	current_user.collection_songs.append(song)
	db.session.add(current_user)
	db.session.commit()
	flash('收藏成功，可在个人中心查看所有收藏歌曲')
	return redirect(url_for('main.singlesong',songid=id))
@main.route('/single/cancelCollect/<int:id>/')
@login_required
def singleCancelCollect(id):
	song = Song.query.get_or_404(id)
	current_user.collection_songs.remove(song)
	db.session.add(current_user)
	db.session.commit()
	flash('已取消收藏')
	return redirect(url_for('main.singlesong',songid=id))
	
