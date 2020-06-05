from hashlib import md5
from datetime import datetime
from app import db,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
	#__tablename__ = user
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(32), index = True, unique = True)
	email = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(256))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	blogs = db.relationship('Blog', backref='author', lazy='dynamic')
	
	def __repr__(self):
		return '<User{}>'.format(self.username)
		
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
		
	def check_password(self,password):
		return check_password_hash(self.password_hash, password)
		
	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
		
		
		
class Blog(db.Model):
	#__tablename__ = blog
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(128), unique=True)
	time_stamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	body = db.Column(db.String(512))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Blog {}>'.format(self.title)
		
@login.user_loader
def load_user(id):
	return User.query.get(int(id))
	
		