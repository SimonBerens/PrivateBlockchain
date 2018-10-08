import json

#  Cryptographic strength constants
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
BOOTNODE = '142.93.4.41'

# Setup dicts of you, users, and nodes
try:
    f = open('me.json', 'r+')
    ME = json.loads(f.read())
    f.close()
    f = open('users.json', 'r+')
    USERS = json.loads(f.read())
    f.close()
    f = open('nodes.json', 'r+')
    NODES = json.loads(f.read())
    f.close()
except ValueError:
    exit('Please use a valid json file')
