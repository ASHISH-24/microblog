from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')
	
class RegisterForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	re_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')
	
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use different Username')
			
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use different Email')
			
class ProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()] )
	about_me = TextAreaField('About me', validators=[Length(min=0, max=256)])
	submit = SubmitField('Update')
	
	def __init__(self, original_username, *args, **kwargs):
		super(ProfileForm,self).__init__(*args, **kwargs)
		self.original_username = original_username
	
	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Use different username!')
				
class FollowForm(FlaskForm):
	submit = SubmitField('Submit')
		