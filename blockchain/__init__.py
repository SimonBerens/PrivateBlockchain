import requests
from flask import Flask

from blockchain.chain_settings import *
from blockchain.classes import *

app = Flask(__name__, instance_relative_config=False)
app.config.from_pyfile('config.py')

me = user_from_dict(ME)

if app.config['MY_URL'] != BOOTNODE:
    USERS = requests.get(f'{BOOTNODE}/api/users').json()
    NODES = requests.get(f'{BOOTNODE}/api/nodes').json()
    log = requests.get(f'{BOOTNODE}/api/nodes').json()
    add_node(BOOTNODE)
    my_chain = blockchain_from_dict(requests.get(f'{BOOTNODE}/api/chain').json())
else:
    my_chain = Blockchain()
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
        requests.post(f'{node}/api/accept_chain',
                      json=to_json(my_chain))


import blockchain.views.client
import blockchain.views.api

