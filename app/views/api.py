from app import flask_app
from flask import jsonify


@flask_app.route
def chain():
    return jsonify({})
