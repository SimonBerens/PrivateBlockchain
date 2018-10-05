from flask import render_template
from package.private_blockchain import app
from package import config


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html', chain_name=config.CHAIN_NAME)
