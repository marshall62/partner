import os
basedir = os.path.abspath(os.path.dirname(__file__))
slashloc = basedir.rindex('/')
projdir = basedir[:slashloc]

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY='temporary_key'
    LOG_FILE='output.log'
    UPLOAD_FOLDER = os.path.join(projdir, 'partner', 'uploads')
    # Amazon RDS db URL should be added here (see docs/secret_stuff.txt)
    SQLALCHEMY_DATABASE_URI = 'postgresql:///partner'
    SQLALCHEMY_TRACK_MODIFICATIONS = True # added to suppress warning - not sure what it does
    CORS_WHITELIST = ["http://localhost:3000"]
    NAME="Config"
    # TERM='spring'  # term and year are set in __init__.py based on env vars or current date
    # YEAR='2020'

class ProductionConfig(Config):
    CORS_WHITELIST = ["http://basic-dm.herokuapp.com", "https://basic-dm.herokuapp.com",
                      "http://pairup-dm.herokuapp.com", "https://pairup-dm.herokuapp.com", "http://localhost:3000"]
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or Config.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    NAME="Production"
    DEBUG = True
    DEVELOPMENT = True

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    NAME="Development"
    # use sqlite until I figure out how to fully deal with postgres when in a term window and need to make python calls to query it
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'partner.db')
    # Database on AWS RDS
    #  TODO Shouldn't this AWS db in ProductionConfig only?  I don't think I'm set up to run a partner db in MySQL locally.

    # SQLALCHEMY_DATABASE_URI = 'postgresql:///partner'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'partner.db')



class TestingConfig(Config):
    TESTING = True
    LOGIN_DISABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CORS_WHITELIST = []
    NAME="Testing"