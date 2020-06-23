from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes #only routes need to be registered with blueprint