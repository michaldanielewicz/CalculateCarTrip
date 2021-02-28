'''
Config for app.py
'''

DATABASE = 'cars'
DATABASE_USERNAME = 'postgres'
DATABASE_PASSWORD = 'password'

DATABASE_URI = 'postgresql://postgres:password@127.0.0.1:5432/cars'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'


class Config():
    """Base config."""
    pass

class ProdConfig():
    """Production config."""
    DEBUG = False
    TESTING = False

class DevConfig():
    """Development config."""
    DEBUG = True
    TESTING = True
    DATABASE_URI 