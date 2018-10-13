import json
import os

import requests
from flask import Flask

from blockchain.classes import *

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
MY_URL = f'{app.config["PROTOCOL"]}://{app.config["HOST"]}:{app.config["PORT"]}'

# Setup nodes
if os.path.exists('nodes.json'):
    with open('nodes.json', 'r') as f:
        try:
            NODES = json.load(f.read())
        except ValueError:
            exit('Please provide a valid nodes file')
else:
    with open('nodes.json', 'w+') as f:
        nodes_str = f'["{BOOTNODE}", "{MY_URL}"]'
        NODES = json.loads(nodes_str)
        f.write(nodes_str)

# Setup self
if os.path.exists('me.json'):
    with open('me.json', 'r') as f:
        try:
            me = user_from_dict(json.load(f.read()))
        except ValueError:
            exit('Please provide a valid me file')
else:
    with open('me.json', 'w+') as f:
        me_str = f'{{"alias": "Anon", "hashed_id": "0", "private_key": "null", "public_key": "null"}}'
        me = user_from_dict(json.loads(me_str))
        me.generate_key_pair()
        f.write(to_json(me))


# Setup users
if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
        try:
            USERS = json.load(f.read())
        except ValueError:
            exit('Please provide a valid users file')
else:
    exit('For this to function you need a premade users file')

my_chain = Blockchain()
genesis_transaction = Transaction(me, me, TRANSACTION_MIN_VALUE, TOTAL_TRANSACTION_FEE)
me.sign(genesis_transaction)
my_chain.transactions.append(genesis_transaction)
log = []


def mine_transactions():
    prev_hash = '0' * DIFFICULTY if len(my_chain.chain) == 0 else my_chain.chain[-1].prev_hash
    block = Block(prev_hash=prev_hash,
                  miner=me,
                  transactions=my_chain.transactions)
    block.mine()
    me.sign(block)
    my_chain.chain.append(block)
    my_chain.transactions = []
    for node in NODES:
        if node != MY_URL:
            requests.post(f'{node}/api/accept_blockchain',
                          json=to_json(my_chain))


import blockchain.views.client
import blockchain.views.api

mine_transactions()
