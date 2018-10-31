from Cryptodome.PublicKey import RSA
from json import dumps
with open("me.json", "w+") as f:
    temp = dict()
    temp['alias'] = input("Your alias: ")
    temp['hashed_id'] = input("Your hashed id: ")
    temp['unhashed_id'] = input("Your unhashed id: ")
    k = RSA.generate(2048)
    temp['public_key'] = k.publickey().export_key().decode()
    temp['private_key'] = k.export_key().decode()
    f.write(dumps(temp))

with open("users.json", "w+") as f:
    f.write("[]")

with open("nodes.json", "w+") as f:
    f.write("[]")
