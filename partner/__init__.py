from flask import Flask

# per Flask doc, we hardcode the application package rather than use __name__
app = Flask('matcher')

from partner import routes