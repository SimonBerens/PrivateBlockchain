from blockchain import app, chain, nodes, users
from blockchain.classes import *
from flask import jsonify, request
from config import LENGTH_DIFFERENCE


#  GET requests go here
@app.route('/api/chain', methods=['GET'])
def get_chain():
    return jsonify(to_dict(chain)), 200


@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    return jsonify(nodes), 200


@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)


#  POST requests go here
@app.route('/api/spread_chain', methods=['POST'])
def compare_blockchains():
    other = Blockchain(json.loads(request.form.get('chain')),
                       json.loads(request.form.get('transactions')))
    if not other.is_valid():
        return jsonify({"message": "Invalid Blockchain"}), 1000
    elif len(other.chain) >= LENGTH_DIFFERENCE:
        chain = other
    else:
        return jsonify({"message": "We are not willing to take your chain"})
