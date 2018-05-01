# Configs
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# All Config vars will be stored in this object
class Config(object):
	# Secret for WTForms
	SECRET_KEY = os.environ.get('SECRET_KEY') or '12345'
	# SQLAlchemy
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	POSTS_PER_PAGE = 5 # Maximum number of Posts per page
