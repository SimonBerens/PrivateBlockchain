import requests
import os
import json
from flask import Flask

from blockchain.chain_settings import *

# Setup self
if os.path.exists('me.json'):
    with open('me.json', 'r') as f:
        try:
            ME = json.load(f)
        except ValueError:
            exit('Please provide a valid me.json file')
else:
    exit('Please provide a me.json')


def add_node(node):
    if node in NODES:
        return False
    else:
        NODES.append(node)


if not START_FROM_BOOTNODE:
    # Setup nodes
    if os.path.exists('nodes.json'):
        with open('nodes.json', 'r') as f:
            try:
                NODES = json.load(f)
            except ValueError:
                exit('Please provide a valid nodes.json')
    else:
        exit('Please provide a nodes.json')

    # Setup users
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            try:
                USERS = json.load(f)
            except ValueError:
                exit('Please provide a valid users.json')
    else:
        exit('Please provide a users.json')
    log = []
else:
    USERS = requests.get(f'{BOOTNODE}/api/users').json()
    NODES = requests.get(f'{BOOTNODE}/api/nodes').json()
    log = requests.get(f'{BOOTNODE}/api/nodes').json()


from blockchain.classes import *

app = Flask(__name__, instance_relative_config=False)
app.config.from_pyfile('config.py')

me = user_from_dict(ME)

if START_FROM_BOOTNODE:
    my_chain = blockchain_from_dict(requests.get(f'{BOOTNODE}/api/chain').json())
else:
    my_chain = Blockchain()

import blockchain.views.client
import blockchain.views.api

