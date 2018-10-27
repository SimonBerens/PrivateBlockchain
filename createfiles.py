from Cryptodome.PublicKey import RSA
from json import dumps
with open("me.json", "w+") as f:
    temp = dict()
    temp['alias'] = 'Anon'
    temp['hashed_id'] = 'Temp'
    temp['unhashed_id'] = 'Temp'
    k = RSA.generate(2048)
    temp['public_key'] = k.publickey().export_key().decode()
    temp['private_key'] = k.export_key().decode()
    f.write(dumps(temp))

with open("users.json", "w+") as f:
    f.write("[]")

with open("nodes.json", "w+") as f:
    f.write("[]")
