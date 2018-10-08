import requests
from flask import Flask

from blockchain.classes import *

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
MY_URL = f'{app.config["PROTOCOL"]}://{app.config["HOST"]}:{app.config["PORT"]}'

my_chain = Blockchain()
me = user_from_dict(ME)
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
