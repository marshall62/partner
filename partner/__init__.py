import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging.handlers
from flask.logging import default_handler
from flask_login import LoginManager
from flask_cors import CORS


basedir = os.path.abspath(os.path.dirname(__file__))
slashloc = basedir.rindex('/')
projdir = basedir[:slashloc]
print("importing partner package")
# per Flask doc, we hardcode the application package rather than use __name__
app = Flask('partner')
app.config.from_pyfile(os.path.join(projdir, 'config.cfg'))
dburl = os.environ.get('DATABASE_URL')
# prefer the environment db url so I can use other dbs in production
if dburl:
    app.config['SQLALCHEMY_DATABASE_URI'] = dburl
# N.B. It may be important to limit the CORS origins so that the fetch API calls can
# pass credentials through cookies (which requires an origin be specified and not be *)
CORS(app, resources={r"/rest/*": 
                        {"origins": ["http://localhost:3000", "http://localhost:8080",
                                "http://localhost:3001", 
                                "https://pairup-dm.herokuapp.com",
                                "http://pairup-dm.herokuapp.com"],   
                        "supports_credentials": True
                        },
                    r"/api/*":
                        {"origins": ["http://localhost:3000","http://localhost:8080",
                        "http://basic-dm.herokuapp.com", "https://basic-dm.herokuapp.com"
                        "http://pairup-dm.herokuapp.com", "https://pairup-dm.herokuapp.com"],
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


