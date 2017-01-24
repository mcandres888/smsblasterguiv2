# configuration

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'sms888'
    USERNAME = None
    PASSWORD = None
    DBTYPE = 'mysql'
    DBHOST = None
    DBNAME = None
    DBUSER = None
    DBPASS = None


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    BASE_URL = 'http://localhost:5984'
    DBHOST = 'localhost'
    DBNAME = 'smsd'
    DBUSER = 'root'
    DBPASS = 'root'

class TestingConfig(Config):
    TESTING = True
