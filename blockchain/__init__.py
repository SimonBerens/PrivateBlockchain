import requests
from flask import Flask

from blockchain.chain_settings import *
from blockchain.classes import *

app = Flask(__name__, instance_relative_config=False)
app.config.from_pyfile('config.py')

me = user_from_dict(ME)
try:
    me.generate_key_pair()
except AssertionError:
    pass

for user in USERS:
    if user['hashed_id'] == me.hashed_id:
        if 'public_key' not in user:
            user['public_key'] = me.public_key
            user['alias'] = me.alias

if app.config['MY_URL'] != BOOTNODE:
    add_node(BOOTNODE)

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
        requests.post(f'{node}/api/accept_blockchain',
                      json=to_json(my_chain))


import blockchain.views.client
import blockchain.views.api

mine_transactions()
