import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging.handlers
from flask.logging import default_handler
from flask_login import LoginManager
from flask_cors import CORS
import datetime


basedir = os.path.abspath(os.path.dirname(__file__))
slashloc = basedir.rindex('/')
projdir = basedir[:slashloc]
print("importing partner package")
# per Flask doc, we hardcode the application package rather than use __name__
app = Flask('partner')

# Correct configuration is per setting of FLASK_ENV environment variable.  CHoices: Production, Development, Testing
# Will use a class in the partner.config.py module


# MUST SET APP_SETTINGS environment var to one of config.ProductionConfig or config.DevelopmentConfig (see config.py)
# on the dev environment this is set in .env
# on heroku this is set by CLI: heroku config:set APP_SETTINGS=config.ProductionConfig
config_class = os.environ['APP_SETTINGS']
print("Using config class" + os.environ['APP_SETTINGS'])
app.config.from_object(config_class)
print("Config name: " + app.config['NAME'] + " read")
now = datetime.datetime.now()
# figure out the term and year based on current date but can override with environment vars if wanting something specific.
app.config['TERM'] = os.environ.get('TERM') or ('spring' if now.month < 6 else 'fall')
app.config['YEAR'] = os.environ.get('YEAR') or str(now.year)


# N.B. It may be important to limit the CORS origins so that the fetch API calls can
# pass credentials through cookies (which requires an origin be specified and not be *)
CORS(app, resources={r"/rest/*": 
                        {"origins": app.config['CORS_WHITELIST'],
                        "supports_credentials": True
                        },
                    r"/api/*":
                        {"origins": app.config['CORS_WHITELIST'],
                        "supports_credentials": True}
                        });
login_manager = LoginManager(app)
login_manager.init_app(app)
# db = SQLAlchemy(app,session_options={"autoflush": False})
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.logger.removeHandler(default_handler)
formatter = logging.Formatter(datefmt='%Y-%m-%d %H:%M:%S,uuu')
fh = logging.handlers.RotatingFileHandler(filename=app.config['LOG_FILE'], mode='a', maxBytes=1 * 1000 * 1000,
                                          backupCount=20)
fh.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: [in %(pathname)s:%(lineno)d] %(threadName)s %(message)s'))
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: [in %(pathname)s:%(lineno)d] %(message)s'))
ch.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
# We always have a file for a log of errors.  Also log to console
app.logger.addHandler(ch)
app.logger.addHandler(fh)
app.logger.debug("Starting app")
app.logger.debug("---------------------------------------------------------")
from partner import routes, rest_routes, models


#  the below is here so I can go to venv shell and do
# flask shell and have all the db objects in the python environment
# >>> somestuff = Student.query.all()
from partner.models import Section,Roster,Student,Group,AttendanceEntry

@app.shell_context_processor
def make_shell_context():
    print("I dont believe this is running")
    return {'db': db, 'Section': Section, 'Roster': Roster, 'Student': Student,
            'Group': Group, 'AttendanceEntry': AttendanceEntry}


