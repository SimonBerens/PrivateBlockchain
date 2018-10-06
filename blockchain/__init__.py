from flask import Flask
import config
from blockchain.classes import *


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
me = user_from_dict(config.ME)
chain = Blockchain()
chain.genesis(me)
nodes = config.NODES
users = config.USERS

import blockchain.views.client
import blockchain.views.api
