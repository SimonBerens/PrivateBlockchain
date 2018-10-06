from flask import Flask
import config
from blockchain.classes import *


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
me = user_from_json_str(config.ME)
me.generate_key_pair()
chain = Blockchain()
chain.genesis(me)
nodes = {f'{config.HOST}:{config.PORT}'}
users = [to_dict(me.public_version())]

import blockchain.views.client
import blockchain.views.api
