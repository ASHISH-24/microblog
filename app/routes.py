from flask import render_template, flash, redirect, url_for, request
from app import app,db,login
from app.forms import *
from app.models import *
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()	

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])

def index():
	form = BlogForm()
	
	if form.validate_on_submit():
		blog = Blog(body=form.content.data, author=current_user)
		db.session.add(blog)
		db.session.commit()
		flash('Posted successfully')
		return redirect(url_for('index'))
	
	'''if not current_user.is_anonymous:
		f_blogs = current_user.followed_posts().all()
	else:'''
	f_blogs = Blog.query.order_by(Blog.time_stamp.desc()).all()
	
	return render_template('index.html', title='TP-Home', form=form, blogs=f_blogs)
	
#@app.route('/login')
@app.route('/index/login', methods = ['GET','POST'])

def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	
	form = LoginForm()
	
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or user.check_password(form.password.data) == False:
			flash('invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		
		'''next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')'''
		return redirect(url_for('index'))
			
	return render_template('login.html', title='TP-SignIn', form=form)

#@app.route('/signup', methods = ['GET', 'POST'])	
@app.route('/index/signup', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations! You are now a registered User.')
		return redirect(url_for('login'))
		
	return render_template('register.html', title='TP-Register', form=form)
	
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))
	
@app.route('/index/blogs')
@login_required
def blogs():
	posts = []
	users = User.query.all()
	for user in users:
		post = user.blogs.all()
		for post_ in post:
			posts.append(post_)
	
	return render_template('blogs.html', title='TP-Blogs', posts=posts)
	
@app.route('/user/<username>')
@login_required
def user(username):
		user = User.query.filter_by(username=username).first_or_404()
		posts = user.blogs.order_by(Blog.time_stamp.desc()).all()
		form = FollowForm()
		
		return render_template('user.html', posts=posts, user=user, form=form)
		
@app.route('/user/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = ProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your Profile is updated successfully.')
		return redirect(url_for('user', username=current_user.username))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
		
	return render_template('edit_profile.html', title='TP-Profile_edit', form=form)
	
@app.route('/follow/<username>', methods = ['POST'])
@login_required
def follow(username):
	form = FollowForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = username).first()
		if user is None:
			flash("User don't exist")
			return redirect(url_for('index'))
		elif user == current_user:
			flash('You can not follow yourself')
			return redirect(url_for('index'))
		current_user.follow(user)
		db.session.commit()
		flash('You successfully followed {}'.format(user.username))
		return redirect(url_for('user', username=username ))
	else:
		return redirect(url_for('index'))
		
@app.route('/unfollow/<username>', methods = ['POST'])
@login_required
def unfollow(username):
	form = FollowForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = username).first()
		if user is None:
			flash("User don't exist")
			return redirect(url_for('index'))
		elif user == current_user:
			flash('You can not unfollow yourself')
			return redirect(url_for('index'))
		current_user.unfollow(user)
		db.session.commit()
		flash('You successfully unfollowed {}'.format(user.username))
		return redirect(url_for('user', username=username ))
	else:
		return redirect(url_for('index'))

		