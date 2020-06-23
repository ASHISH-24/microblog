from hashlib import md5
from datetime import datetime
from app import db,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
from flask import url_for, current_app

followers = db.Table('followers',
			db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
			db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
			)

class PaginatedAPIMixin(object):
	@staticmethod
	def to_collection_dict(query, page, per_page, endpoint, **kwargs):
		resources = query.paginate(page, per_page, False)
		data = {
			'items': [item.to_dict() for item in resources.items],
			'_meta': {
				'page': page,
				'per_page': per_page,
				'total_pages': resources.pages,
				'total_items': resources.total
				},
			'_links': {
				'self':url_for(endpoint, page=page, per_page=per_page, **kwargs),
				'next':url_for(endpoint, page=page+1, per_page=per_page,\
						**kwargs) if resources.has_next else None,
				'prev':url_for(endpoint, page=page-1, per_page=per_page,\
						**kwargs) if resources.has_next else None
				}	
		}
		
		return data	

class User(UserMixin, db.Model, PaginatedAPIMixin):
	#__tablename__ = user
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(32), index = True, unique = True)
	email = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(256))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	
	blogs = db.relationship('Blog', backref='author', lazy='dynamic')
	
	followed = db.relationship(
				'User', secondary=followers,
				 primaryjoin=(followers.c.follower_id == id),
				 secondaryjoin=(followers.c.followed_id == id),
				 backref=db.backref('followers', lazy='dynamic'),
				 lazy='dynamic')
				 
	def __repr__(self):
		return '<User{}>'.format(self.username)
		
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
		
	def check_password(self,password):
		return check_password_hash(self.password_hash, password)
		
	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
		
	def follow(self,user):
		if not self.is_following(user):
			self.followed.append(user)
			
	def unfollow(self,user):
		if self.is_following(user):
			self.followed.remove(user)
			
	def is_following(self,user):
		return self.followed.filter(followers.c.followed_id == user.id).count()>0
			
			
	def followed_posts(self):
		followed = Blog.query.join(followers, (followers.c.followed_id == Blog.user_id)).filter(followers.c.follower_id == self.id)
		
		own = Blog.query.filter_by(user_id =self.id)
		return followed.union(own).order_by(Blog.time_stamp.desc())
			
	def to_dict(self, include_email=False):
		data = {
			'id': self.id,
			'username': self.username,
			'last_seen': self.last_seen.isoformat() + 'Z',
			'about_me': self.about_me,
			'followers_count': self.followers.count(),
			'followed_count': self.followed.count(),
			'_links': {
				'self': url_for('api.get_user', id=self.id),
				'followers': url_for('api.get_followers', id=self.id),
				'followed': url_for('api.get_followed', id=self.id),
				'avatar': self.avatar(128)
				}
			}
		
		if include_email:
			data['email'] = self.email
		return data
		
	def from_dict(self, data, new_user=False):
		for field in ['username', 'email', 'about_me']:
			if field in data:
				setattr(self,field,data[field])
		if new_user and 'password' in data:
			self.set_password(data['password'])
	
	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(\
				{'reset_password': self.id, 'expires_in':time()+ expires_in},\
				current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, current_app.config['SECRET_KEY'],\
			algorithm='HS256')['reset_password']
		except:
			return
		return User.query.get(id)	
			
		
class Blog(db.Model, PaginatedAPIMixin):
	#__tablename__ = blog
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(128), unique=True)
	time_stamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	body = db.Column(db.String(512))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	language = db.Column(db.String(5))
	tag = db.Column(db.String(16))
	
	def __repr__(self):
		return '<Blog {}>'.format(self.title)
		
		
@login.user_loader
def load_user(id):
	return User.query.get(int(id))
	
		