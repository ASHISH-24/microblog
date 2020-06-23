from flask import *
from app import *
from app.main.forms import *
from app.models import *
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from guess_language import guess_language
from app.translate import translate
from app.main import bp
from flask_babel import _, get_locale

@bp.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()	

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])

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
		return redirect(url_for('main.index'))
		
	page  = request.args.get('page', 1, type=int)	
	
	posts = Blog.query.order_by(Blog.time_stamp.desc()).\
			paginate(page, current_app.config['POST_PER_PAGE'], False)
	
	next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
		
	prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
	
	
	return render_template('index.html', title='Home', posts=posts.items,\
							next_url=next_url, prev_url=prev_url, form=form)
	
	
	
@bp.route('/index/explore', methods=['GET','POST'])
@login_required
def explore():
	form = FollowForm()
	users = User.query.all()
	
		
	return render_template('explore.html', title='Explore Blogs',\
							users = users, form = form)
	
@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
	user = User.query.filter_by(username=username).first()
	return render_template('user_popup.html', user=user)
	
@bp.route('/user/<username>')
@login_required
def user(username):
		user = User.query.filter_by(username=username).first_or_404()
		
		page = request.args.get('page',1,type=int)
		posts = user.blogs.order_by(Blog.time_stamp.desc())\
				.paginate(page, current_app.config['POST_PER_PAGE'], False)
				
		next_url = url_for('main.user', username=user.username, page=posts.next_num)\
					if posts.has_next else None
					
		prev_url = url_for('main.user', username=user.username, page=posts.prev_num)\
					if posts.has_prev else None
		
		form = FollowForm()
		
		return render_template('user.html', posts=posts.items, user=user,\
					form=form, next_url=next_url, prev_url=prev_url)
		
@bp.route('/user/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = ProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your Profile is updated successfully.')
		return redirect(url_for('main.user', username=current_user.username))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
		
	return render_template('edit_profile.html', title='Profile_edit', form=form)
	
@bp.route('/follow/<username>', methods = ['POST'])
@login_required
def follow(username):
	form = FollowForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = username).first()
		if user is None:
			flash("User don't exist")
			return redirect(url_for('main.index'))
		elif user == current_user:
			flash('You can not follow yourself')
			return redirect(url_for('main.index'))
		current_user.follow(user)
		db.session.commit()
		flash('You successfully followed {}'.format(user.username))
		return redirect(url_for('main.user', username=current_user.username ))
	else:
		return redirect(url_for('main.index'))
		
@bp.route('/unfollow/<username>', methods = ['POST'])
@login_required
def unfollow(username):
	form = FollowForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = username).first()
		if user is None:
			flash("User don't exist")
			return redirect(url_for('main.index'))
		elif user == current_user:
			flash('You can not unfollow yourself')
			return redirect(url_for('main.index'))
		current_user.unfollow(user)
		db.session.commit()
		flash('You successfully unfollowed {}'.format(user.username))
		return redirect(url_for('main.user', username=current_user.username ))
	else:
		return redirect(url_for('main.index'))
		

		
		

		