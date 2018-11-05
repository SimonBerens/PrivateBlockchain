from flask import jsonify, request

from blockchain import *
from blockchain.classes import *


#  GET requests go here
@app.route('/api/chain', methods=['GET'])
def get_chain():
    return jsonify(to_dict(my_chain)), 200


@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    return jsonify(NODES), 200


@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(USERS)


@app.route('/api/user_info', methods=['GET'])
def get_user_info():
    user_id = request.args.get('id')
    if user_id is None:
        return jsonify(message="No user id given"), 408
    hashed_id = hasher(user_id.encode()).hexdigest()
    for user in USERS:
        if user['hashed_id'] == hashed_id:
            try:
                user_from_dict(user)
            except KeyError:
                return jsonify(message="User has not been initialized"), 408
            return jsonify({
                'alias': user['alias'],
                'key': user['public_key'],
                'balance': my_chain.compute_balances()[user['public_key']]
            }), 200
    else:
        return jsonify(message="User not found"), 408


@app.route('/api/log', methods=['GET'])
def get_log():
    return jsonify(log)


@app.route('/api/block_transactions', methods=['GET'])
def get_transaction_from_block():
    block_id = request.args.get('id')
    if block_id is None:
        return jsonify(message="No id given"), 408
    try:
        block_id = int(block_id)
    except ValueError:
        return jsonify(message="Id not an integer"), 408
    if block_id >= len(my_chain.chain):
        return jsonify(message="Id too large"), 408
    if block_id < 0:
        return jsonify(message="Id too small"), 408
    return jsonify(to_dict(my_chain.chain[block_id].transactions)), 200


#  POST requests go here
@app.route('/api/accept_user', methods=['POST'])
def accept_user():
    args = json.loads(request.get_json())
    if 'public_key' not in args:
        return jsonify(message="You did not provide the public key"), 408
    if 'id' not in args:
        return jsonify(message="You did not provide the unhashed id"), 408
    if 'alias' not in args:
        return jsonify(message="You did not provide the alias"), 408
    if 'node_url' not in args:
        return jsonify(message="You did not provide the node url"), 408
    for user in USERS:
        if hasher(args['id'].encode()).hexdigest() == user['hashed_id']:
            if 'public_key' in user:
                return jsonify(message="This user has already been registered"), 408
            else:
                try:
                    RSA.import_key(args['public_key'])
                except (ValueError, IndexError, TypeError) as e:
                    return jsonify(message="Invalid Public Key")
                user['public_key'] = args['public_key']
                user['alias'] = args['alias']
                user['private_key'] = None
                if args['node_url'] != BOOTNODE:
                    add_node(args['node_url'])
                return jsonify(message="Success! User claimed"), 200
    else:
        return jsonify(message="That id did not match any hashed id's"), 408


@app.route('/api/accept_transaction', methods=['POST'])
def accept_transaction():
    args = json.loads(request.get_json())
    try:
        transaction = transaction_from_dict(args)
    except KeyError:
        return jsonify(message="Not all fields are present"), 408
    if not find_user(transaction.sender.public_key):
        return jsonify(message="Sender not found"), 408
    if not find_user(transaction.recipient.public_key):
        return jsonify(message="Recipient not found"), 408
    balances = my_chain.compute_balances()
    balances[transaction.recipient.public_key] += transaction.value
    if balances[transaction.sender.public_key] < transaction.value + transaction.fee:
        return jsonify(message="Not enough balance to send this transaction"), 408
    if transaction.is_valid():
        my_chain.transactions.append(transaction)
        total = BASE_MINER_REWARD
        for transaction in my_chain.transactions:
            total += transaction.fee
        if total >= TOTAL_TRANSACTION_FEE:
            mine_transactions()
        return jsonify(message="Success! Transaction processed!"), 200
    else:
        return jsonify(message="Invalid transaction"), 408


@app.route('/api/accept_chain', methods=['POST'])
def accept_blockchain():
    args = json.loads(request.get_json())
    try:
        other = blockchain_from_dict(args)
    except TypeError:
        return jsonify(message="Stop trying to break things")
    if not other.is_valid():
        return jsonify(message="Invalid Blockchain"), 408
    elif (len(other.chain) - len(my_chain.chain)) >= LENGTH_DIFFERENCE:
        my_chain.chain = other.chain
        return jsonify(message="Success! We have replaced our chain with yours"), 200
    else:
        return jsonify(message="We are not willing to take your chain"), 407


def mine_transactions():
    prev_hash = '0' * DIFFICULTY if len(my_chain.chain) == 0 else my_chain.chain[-1].prev_hash
    block = Block(prev_hash=prev_hash,
                  miner=me,
                  transactions=my_chain.transactions)
    block.mine()
    me.sign(block)
    my_chain.chain.append(block)
    my_chain.transactions = []
    from blockchain.views.client import spread_message
    spread_message('accept_chain', to_json(my_chain), '/', '/', False)
