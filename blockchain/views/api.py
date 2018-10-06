from blockchain import app, classes, chain, nodes, users
from flask import jsonify


#  GET requests go here
@app.route('/api/chain')
def get_chain():
    return jsonify(classes.to_dict(chain)), 200


@app.route('/api/nodes')
def get_nodes():
    return jsonify(nodes), 200


@app.route('/api/users')
def get_users():
    return jsonify(users)
