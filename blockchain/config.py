from Cryptodome.Random import get_random_bytes as rand

PROTOCOL = 'http'
HOST = '67.205.129.210'
PORT = '80'
DEBUG = False
SECRET_KEY = rand(64)
MY_URL = f'{PROTOCOL}://{HOST}:{PORT}'


