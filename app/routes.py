from flask import render_template, flash, redirect, url_for, request, jsonify
from app import *
from app.forms import *
from app.models import *
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from guess_language import guess_language
from app.translate import translate

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
		language = guess_language(form.content.data)
		if language == 'UNKNOWN' or len(language)>5:
			language = ''
		blog = Blog(body = form.content.data, author=current_user,\
					language = language)
		db.session.add(blog)
		db.session.commit()
		flash('Your thought posted successfully!')
		return redirect(url_for('index'))
		
	page  = request.args.get('page', 1, type=int)	
	
	posts = Blog.query.order_by(Blog.time_stamp.desc()).\
			paginate(page, app.config['POST_PER_PAGE'], False)
	
	next_url = url_for('index', page=posts.next_num) if posts.has_next else None
		
	prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
	
	
	return render_template('index.html', title='Home', posts=posts.items,\
							next_url=next_url, prev_url=prev_url, form=form)
	
@app.route('/login', methods=['GET','POST'])
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
		
		next_page = request.args.get('next')
		
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
			
		return redirect(next_page)
			
	return render_template('login.html', title='TP-SignIn', form=form)

@app.route('/signup', methods=['GET','POST'])	
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
	
@app.route('/index/explore', methods=['GET','POST'])
@login_required
def explore():
	form = FollowForm()
	users = User.query.all()
	
		
	return render_template('explore.html', title='Explore Blogs',\
							users = users, form = form)
	
@app.route('/user/<username>/popup')
@login_required
def user_popup(username):
	user = User.query.filter_by(username=username).first()
	return render_template('user_popup.html', user=user)
	
@app.route('/user/<username>')
@login_required
def user(username):
		user = User.query.filter_by(username=username).first_or_404()
		
		page = request.args.get('page',1,type=int)
		posts = user.blogs.order_by(Blog.time_stamp.desc())\
				.paginate(page, app.config['POST_PER_PAGE'], False)
				
		next_url = url_for('user', username=user.username, page=posts.next_num)\
					if posts.has_next else None
					
		prev_url = url_for('user', username=user.username, page=posts.prev_num)\
					if posts.has_prev else None
		
		form = FollowForm()
		
		return render_template('user.html', posts=posts.items, user=user,\
					form=form, next_url=next_url, prev_url=prev_url)
		
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
		
@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
		
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
			flash('Check your email for link to password reset')
			return redirect(url_for('login'))
		else:
			flash('You are not registered with us')
			return redirect(url_for('register'))
			
	return render_template('reset_password_request.html', form=form, title='TP-Password Reset')
	
@app.route('/reset/<token>', methods=['GET','POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
		
	user = User.verify_reset_password_token(token)
	if not user:
		flash('Your token has expired!!')
		return redirect(url_for('login'))
	
	form = ResetPasswordForm()
	
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password changed successfully')
		return redirect(url_for('login'))
		
	return render_template('reset_password.html', form=form)

		
		

		