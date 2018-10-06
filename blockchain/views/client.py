from flask import render_template, request
from blockchain import app, chain
import config


@app.route('/nav')
def append_navbar():
    return render_template(
        template_name_or_list='navbar.html',
        selected=request.args.get('select'),
        chain_name=config.CHAIN_NAME)


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html', block_messages=chain.chain)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/submit')
def submit():
    return render_template('submit.html')

