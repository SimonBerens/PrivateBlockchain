#  Deployment settings
import json

HOST = '0.0.0.0'
PORT = '80'
DEBUG = True

#  Cryptographic strength constants
DIFFICULTY = 2
NUM_KEY_BITS = 2048

#  Transaction conditions for miner to accept blockchain
TRANSACTION_MIN_VALUE = 0
MIN_TRANSACTIONS_IN_BLOCK = 1
LENGTH_DIFFERENCE = 1

#  Name of private blockchain to display in html
CHAIN_NAME = 'Private Blockchain'

#  JSON string of user
f = open('me.json', 'r+')
ME = json.loads(f.read())
f.close()
f = open('users.json', 'r+')
USERS = json.loads(f.read())
f.close()
f = open('nodes.json', 'r+')
NODES = json.loads(f.read())
f.close()


