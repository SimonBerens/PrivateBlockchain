#  Cryptographic strength constants
import json
import os

DIFFICULTY = 1
NUM_KEY_BITS = 2048

#  Blockchain acceptance conditions
TRANSACTION_MIN_VALUE = 0
MIN_TRANSACTIONS_IN_BLOCK = 1
TOTAL_TRANSACTION_FEE = 1
LENGTH_DIFFERENCE = 1
BASE_MINER_REWARD = 10

#  Name of private blockchain to display in html
CHAIN_NAME = 'Private Blockchain'

# Bootnode
BOOTNODE = 'http://67.205.129.210:80'

# Setup nodes
if os.path.exists('nodes.json'):
    with open('nodes.json', 'r') as f:
        try:
            NODES = json.load(f)
        except ValueError:
            exit('Please provide a valid nodes.json')
else:
    exit('Please provide a nodes.json')


def add_node(node):
    if node in NODES:
        return False
    else:
        NODES.append(node)


# Setup self
if os.path.exists('me.json'):
    with open('me.json', 'r') as f:
        try:
            ME = json.load(f)
        except ValueError:
            exit('Please provide a valid me.json file')
else:
    exit('Please provide a me.json')


# Setup users
if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
        try:
            USERS = json.load(f)
        except ValueError:

            exit('Please provide a valid users.json')
else:
    exit('Please provide a users.json')
