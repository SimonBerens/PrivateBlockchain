import json
from dataclasses import dataclass
from time import time
from datetime import datetime
from Cryptodome.Signature import pkcs1_15
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA3_512
from typing import List
from copy import deepcopy
from private_blockchain.settings import ME, DIFFICULTY, TRANSACTION_MIN, NUM_KEY_BITS


def to_dict(obj, omit_signature=False):
    """
    Recursively goes through fields and adds them to dictionary
    :param omit_signature: whether or not to take the signature into account
    :param obj: User, Transaction, Block, or Blockchain object
    :return: a dictionary representation of obj
    """
    t = type(obj)
    assert t == User or t == Transaction or t == Block or t == Blockchain, \
        'You cannot call this function on unapproved types'
    dictified = dict()
    for name, value in obj.__dict__.items():
        tv = type(value)
        if tv == User or tv == Transaction or tv == Block or tv == Blockchain:
            dictified[name] = to_dict(value.public_version(), omit_signature)
        else:
            dictified[name] = value
    if t != User and t != Blockchain and omit_signature:
        dictified['signature'] = None
    return dictified


def to_json(obj, omit_signature=False):
    """
    Converts obj to dictionary and then turns that into a string
    :param omit_signature: whether or not to take the signature into account
    :param obj: User, Transaction, Block, or Blockchain object
    :return: string representation of obj
    """
    t = type(obj)
    assert t == User or t == Transaction or t == Block or t == Blockchain, \
        'You cannot call this function on unapproved types'
    return json.dumps(to_dict(obj, omit_signature), sort_keys=True)


def hasher(obj):
    """
    :param obj: object to return updated hasher of
    :return: SHA3_512 hasher object
    """
    t = type(obj)
    assert t == Transaction or t == Block or t == bytes, \
        'You cannot call this function on unapproved types'
    return SHA3_512.new().update(obj if t == bytes else to_json(obj, omit_signature=True).encode())


def valid_signature(obj):
    """
    :param obj: a Transaction or Block object
    :return: if the signature is valid
    """
    t = type(obj)
    if t == Transaction:
        public_key = RSA.import_key(obj.sender.public_key)
    elif t == Block:
        public_key = RSA.import_key(obj.miner.public_key)
    else:
        raise AssertionError('Object is not of Transaction or Block type')
    assert obj.signature is not None, 'A ' + str(t.__name__) + ' cannot be valid without a signature'
    verifier = pkcs1_15.new(public_key)
    try:
        verifier.verify(hasher(obj), obj.signature)
    except ValueError:
        return False
    return True


def timestamp(obj):
    """
    :param obj: object to timestamp field 'time'
    :return:
    """
    t = type(obj)
    assert t == Transaction or t == Block, \
        'You cannot call this function on unapproved types'
    assert obj.time is None, 'This ' + str(t.__name__) + ' has already been timestamped'
    obj.time = datetime.utcfromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


@dataclass
class User:
    """
    Class for storing user info
    Only use the private_key field if the user is you
    """
    alias: str
    hashed_id: str
    public_key: str = None
    private_key: str = None

    def __post_init__(self):
        if self.public_key == 'None':
            self.public_key = None
        if self.private_key == 'None':
            self.private_key = None

    def generate_key_pair(self):
        assert self.public_key is None, 'This user already has a public key'
        assert self.private_key is None, 'This user already has a private key'
        key_pair = RSA.generate(NUM_KEY_BITS)
        self.private_key = key_pair.export_key().decode()
        self.public_key = key_pair.publickey().export_key().decode()

    def sign(self, obj):
        """
        Only use for when you have the private key
        :param obj: Block or Transaction to sign
        """
        t = type(obj)
        assert t == Transaction or t == Block, \
            'You cannot call this function on unapproved types'
        assert obj.signature is None, 'This ' + str(t.__name__) + ' is already signed'
        key = RSA.import_key(self.private_key)
        assert RSA.RsaKey.has_private(key), 'Invalid private key'
        signer = pkcs1_15.new(key)
        obj.signature = signer.sign(hasher(obj))

    def public_version(self):
        copy = deepcopy(self)
        copy.private_key = None
        return copy


def user_from_json(user_json_str):
    """
    :param user_json_str: json.loads-ifiable string
    :return: User object
    """
    user_dict = json.loads(user_json_str)
    return User(alias=user_dict['alias'],
                hashed_id=user_dict['hashed_id'],
                public_key=user_dict['public_key'],
                private_key=user_dict['private_key'])


@dataclass
class Transaction:
    """
    Class for storing transactions to allow for easy verification
    """
    sender: User
    recipient: User
    value: float
    time: str = None
    signature: str = None

    def __post_init__(self):
        if self.time is None:
            timestamp(self)

    def public_version(self):
        copy = deepcopy(self)
        copy.sender.private_key = None
        copy.recipient.private_key = None
        return copy

    def is_valid(self):
        """
        :return: if the signature and value are valid
        """
        if not valid_signature(self):
            return False
        if self.value <= TRANSACTION_MIN:
            return False
        return True


def transaction_from_json(transaction_json):
    """
    :param transaction_json: jsonified Transaction object
    :return: Transaction object
    """
    return Transaction(sender=user_from_json(transaction_json['miner']),
                       recipient=user_from_json(transaction_json['recipient']),
                       value=transaction_json['value'],
                       time=transaction_json['time'],
                       signature=transaction_json['signature'])


@dataclass
class Block:
    """
    Block class where the default constructor returns the genesis block
    """
    prev_hash: str
    transactions: List[Transaction]
    miner: User
    time: str = None
    nonce: int = 0
    signature: str = None

    def __post_init__(self):
        timestamp(self)

    def public_version(self):
        """
        :return: Block stripped of miner's private_key
        """
        copy = deepcopy(self)
        copy.miner.private_key = None
        return copy

    def transactions_valid(self):
        for transaction in self.transactions:
            if not transaction.is_valid():
                return False
        return True

    def difficulty_valid(self, premade_json_str=None):
        for_mining = premade_json_str is not None
        if for_mining:
            h = hasher(premade_json_str.encode()).hexdigest()
        else:
            h = hasher(self).hexdigest()
        return h[:DIFFICULTY] == '0' * DIFFICULTY

    def is_valid(self):
        """
        :return: if all the transactions are valid,
                    the signature is valid,
                    and the hash has appropriate proof of work
        """
        return self.difficulty_valid() and \
               valid_signature(self) and \
               self.transactions_valid()

    def mine(self):
        assert self.signature is None, 'You cannot mine a signed block'
        assert self.transactions_valid(), 'You cannot mine an invalid block'
        assert self.nonce == 0, 'The nonce has already been modified'
        premade_json_str = to_json(self)
        nonce_str = '"nonce": '
        nonce_index = int(premade_json_str.find(nonce_str)) + len(nonce_str)
        nonce = 0
        while not self.difficulty_valid(premade_json_str):
            premade_json_str = premade_json_str[:nonce_index] + \
                               premade_json_str[nonce_index:].replace(str(nonce), str(nonce + 1), 1)
            nonce += 1
        self.nonce = nonce


def block_from_json(block_json):
    return Block(prev_hash=block_json['prev_hash'],
                 time=block_json['time'],
                 transactions=block_json['transactions'],
                 miner=user_from_json(block_json['miner']),
                 nonce=block_json['nonce'],
                 signature=block_json['signature'])


@dataclass
class Blockchain:
    chain: List[Block] = None
    owner: User = user_from_json(ME)
    transactions: List[Transaction] = None

    def __post_init__(self):
        """
        Generates genesis block
        """
        if self.transactions is None:
            self.transactions = []
        if self.owner.public_key is None and self.owner.private_key is None:
            self.owner.generate_key_pair()
        if self.chain is None:
            block = Block('0' * DIFFICULTY, [], self.owner)
            block.mine()
            self.owner.sign(block)
            self.chain = [block]

    def is_valid(self):
        """
        :return: if all the blocks are valid
                and the hash pointers are correct
        """
        genesis = self.chain[0]
        if not genesis.is_valid():
            return False
        prev_block = genesis
        for block in self.chain[1:]:
            if not block.is_valid():
                return False
            if hasher(prev_block).hexdigest() != block.prev_hash:
                return False
            prev_block = block
        return True

    def submit_transaction(self, transaction):
        assert transaction.is_valid()
        self.transactions.append(transaction)


def blockchain_from_json(blockchain_json_str):
    """
    :param blockchain_json_str: jsonified blockchain string
    :return: Blockchain object
    """
    blockchain_json = json.loads(blockchain_json_str)
    return Blockchain(chain=blockchain_json['chain'])


c = Blockchain()
print(c.is_valid())
