from flask import request
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from app.models import User
from flask_babel import _, lazy_gettext as _l
			
class ProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()] )
	about_me = TextAreaField('About me', validators=[Length(min=0, max=256)])
	submit = SubmitField('Update')
	
	def __init__(self, original_username, *args, **kwargs):
		super(ProfileForm,self).__init__(*args, **kwargs)
		self.original_username = original_username
	
	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Use different username!')
				
class FollowForm(FlaskForm):
	submit = SubmitField('Submit')
	
class BlogForm(FlaskForm):
	content = TextAreaField('Say Something', validators=[DataRequired(), Length(min=0, max=512)])
	tag = StringField('Tag', validators=[DataRequired()])
	submit = SubmitField('Post')	
