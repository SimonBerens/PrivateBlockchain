from flask import Flask

flask_app = Flask(__name__, instance_relative_config=True)
flask_app.config.from_pyfile('config.py')
import app.views.client
