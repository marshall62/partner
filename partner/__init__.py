from flask import Flask
from flask_login import LoginManager

# per Flask doc, we hardcode the application package rather than use __name__
app = Flask('matcher')
login = LoginManager(app)
from partner import routes