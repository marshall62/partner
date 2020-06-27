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
    # TERM='spring'  # term and year are set in __init__.py based on env vars or current date
    # YEAR='2020'

class ProductionConfig(Config):
    CORS_WHITELIST = ["http://basic-dm.herokuapp.com", "https://basic-dm.herokuapp.com",
                      "http://pairup-dm.herokuapp.com", "https://pairup-dm.herokuapp.com"]

class DevelopmentConfig(Config):
    DEBUG = True
    # use sqlite until I figure out how to fully deal with postgres when in a term window and need to make python calls to query it
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'partner.db')
    # Database on AWS RDS
    #  TODO Shouldn't this AWS db in ProductionConfig only?  I don't think I'm set up to run a partner db in MySQL locally.
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:jupiter62@flask-aws-tutorial-db.cmnye3vldx70.us-east-2.rds.amazonaws.com/pairup'
    SQLALCHEMY_DATABASE_URI = 'postgresql:///partner'



class TestingConfig(Config):
    TESTING = True
    LOGIN_DISABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CORS_WHITELIST = []