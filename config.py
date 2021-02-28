'''
Config for app.py
'''

import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    """Base config."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(Config):
    """Production config."""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class DevConfig(Config):
    """Development config."""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ['LOCAL_DATABASE_URI']
