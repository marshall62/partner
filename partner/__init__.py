import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
basedir = os.path.abspath(os.path.dirname(__file__))

print("importing partner package")
# per Flask doc, we hardcode the application package rather than use __name__
app = Flask('matcher')
app.config.from_pyfile(os.path.join(basedir, 'config.cfg'))
login = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from partner import routes