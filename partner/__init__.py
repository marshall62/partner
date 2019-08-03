import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging.handlers
from flask.logging import default_handler
basedir = os.path.abspath(os.path.dirname(__file__))
slashloc = basedir.rindex('/')
projdir = basedir[:slashloc]
print("importing partner package")
# per Flask doc, we hardcode the application package rather than use __name__
app = Flask('partner')
app.config.from_pyfile(os.path.join(projdir, 'config.cfg'))
login = LoginManager(app)
db = SQLAlchemy(app,session_options={"autoflush": False})
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
# We always have a file for a log of errors.  In dev environment, also log to console
if app.config['ENV'] == 'development':
    app.logger.addHandler(ch)
app.logger.addHandler(fh)
app.logger.debug("Starting app")
app.logger.debug("---------------------------------------------------------")
from partner import routes, models