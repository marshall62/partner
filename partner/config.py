from partner import projdir,basedir
import os
class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY='temporary_key'
    LOG_FILE='output.log'
    UPLOAD_FOLDER = os.path.join(projdir, 'partner', 'uploads')
    SQLALCHEMY_DATABASE_URI = 'postgresql:///partner'
    SQLALCHEMY_TRACK_MODIFICATIONS = True # added to suppress warning - not sure what it does
    CORS_WHITELIST = ["http://localhost:3000"]

class ProductionConfig(Config):
    CORS_WHITELIST = ["http://basic-dm.herokuapp.com", "https://basic-dm.herokuapp.com",
                      "http://pairup-dm.herokuapp.com", "https://pairup-dm.herokuapp.com"]

class DevelopmentConfig(Config):
    DEBUG = True
    # CUrrently there is no Production deploy so I want my db to be postgres
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')


class TestingConfig(Config):
    TESTING = True
    LOGIN_DISABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CORS_WHITELIST = []