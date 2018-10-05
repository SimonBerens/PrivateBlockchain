from flask import Flask

app = Flask(__name__, instance_relative_config=True)
import package.private_blockchain.views
app.config.from_pyfile('config.py')

