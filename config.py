from Cryptodome.Random import get_random_bytes as rand

PROTOCOL = 'http'
HOST = '0.0.0.0'
PORT = '80'
DEBUG = False
SECRET_KEY = rand(64)
