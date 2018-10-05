from flask import render_template
from app import flask_app
import config


@flask_app.route('/')
@flask_app.route('/index')
@flask_app.route('/index.html')
def index():
    return render_template('index.html', chain_name=config.CHAIN_NAME)
