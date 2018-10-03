import json
from dataclasses import dataclass
from time import time
from datetime import datetime
from Cryptodome import Signature, PublicKey
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA3_512
from typing import List
from copy import deepcopy

from config import ME, DIFFICULTY


# thanks stack overflow
def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


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

    def generate_key_pair(self):
        assert self.public_key is None, 'This user already has a public key'
        assert self.private_key is None, 'This user already has a private key'
        key_pair = RSA.generate(2048)
        self.private_key = key_pair.export_key().decode()
        self.public_key = key_pair.publickey().export_key().decode()

    def sign(self, message):
        """
        Only use for when you have the private key
        :param message: message to sign
        :return: signature for message
        """
        key = RSA.import_key(self.private_key)
        assert RSA.RsaKey.has_private(key), 'Invalid private key'
        signer = Signature.pkcs1_15.new(key) # todo: runtime module attribute error?
        hasher = SHA3_512.new().update(message)
        return signer.sign(hasher)

    def to_json(self):
        """
        :return: jsonified User WITHOUT private_key
        """
        copy = deepcopy(self)
        copy.private_key = None
        return json.dumps(todict(copy), sort_keys=True).encode()


def user_from_json(user_json):
    """
    :param user_json: User WITHOUT private_key
    :return: User object
    """
    return User(alias=user_json['alias'],
                hashed_id=user_json['hashed_id'],
                public_key=user_json['public_key'] if 'public_key' in user_json else None)


def valid_signature(obj):
    """
    :param obj: a Transaction or Block object
    :return: if the signature is valid
    """
    if type(obj) == Transaction:
        public_key = PublicKey.RSA.import_key(obj.sender.public_key)
    elif type(obj) == Block:
        public_key = PublicKey.RSA.import_key(obj.miner.public_key)
    else:
        raise AssertionError('Object is not of Transaction or Block type')
    verifier = Signature.pkcs1_15.new(public_key)
    hasher = SHA3_512.new().update(obj.to_json())
    try:
        verifier.verify(hasher, obj.signature)
    except ValueError:
        return False
    return True


def timestamp():
    return datetime.utcfromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


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
        """
        Checks if it was created from JSON or by itself
        If created by itself, it timestamps and signs itself
        This requires the miner to be the owner and having a valid private key
        """
        self.sender = deepcopy(self.sender)
        self.recipient = deepcopy(self.recipient)
        if self.time is None:
            self.time = timestamp()
        if self.signature is None:
            self.sign()

    def sign(self):
        """
        The miner (assuming they have a valid private key) signs the transaction
        This is a one time operation, you cannot re-sign a transaction
        """
        assert self.signature is None, 'This transaction is already signed'
        self.signature = self.sender.sign(self.to_json())
        self.sender.private_key = None

    def is_valid(self):
        """
        :return: if the signature and value are valid
        """
        if not valid_signature(self):
            return False
        if self.value <= 0:
            return False
        return True

    def to_json(self):
        """
        :return: jsonified Transaction
        """
        assert self.sender.private_key is None, 'You are trying to jsonify with a private key'
        return json.dumps(todict(self), sort_keys=True).encode()


def transaction_from_json(transaction_json):
    """
    :param transaction_json: jsonified Transaction object
    :return: Transaction object
    """
    return Transaction(sender=user_from_json(transaction_json['miner']),
                       recipient=user_from_json(transaction_json['recipient']),
                       value=transaction_json['value'],
                       time=transaction_json['time'] if 'time' in transaction_json else None,
                       signature=transaction_json['signature'] if 'signature' in transaction_json else None)


@dataclass
class Block:
    """
    Block class where the default constructor returns the genesis block
    """
    prev_hash: str = '0' * DIFFICULTY
    transactions: List[Transaction] = None
    miner: User = user_from_json(ME)
    time: str = None
    nonce: int = 0
    signature = None

    def __post_init__(self):
        if self.transactions is None:
            self.transactions = []
        self.miner = deepcopy(self.miner)
        if self.miner.private_key is None and self.miner.public_key is None:
            self.miner.generate_key_pair()
        if time is None:
            self.time = timestamp()
        if self.nonce is 0:
            self.mine()
        if self.signature is None:
            self.sign()

    def hash(self, for_mining=True):
        """
        :param for_mining: set to true if you
        :return:
        """
        # small cpu optimization
        if for_mining:
            return SHA3_512.new().update(self.to_json()).hexdigest()
        else:
            copy = deepcopy(self)
            copy.signature = None
            return SHA3_512.new().update(copy.to_json()).hexdigest()

    def sign(self):
        """
        :return: signature of block without signature
        """
        assert self.signature is None, 'This block is already signed'
        private_key, self.miner.private_key = self.miner.private_key, None
        jsonified = self.to_json()
        self.miner.private_key = private_key
        self.signature = self.miner.sign(jsonified)

    def transactions_valid(self):
        for transaction in self.transactions:
            if not transaction.is_valid():
                return False
        return True

    def difficulty_valid(self, for_mining=True):
        return self.hash(for_mining)[:DIFFICULTY] == '0' * DIFFICULTY

    def is_valid(self):
        """
        :return: if all the transactions are valid,
                    the signature is valid,
                    and the hash has appropriate proof of work
        """
        return self.difficulty_valid(for_mining=False) and \
            valid_signature(self) and \
            self.transactions_valid()

    def mine(self):
        assert self.transactions_valid(), 'You cannot mine an invalid block'
        private_key, self.miner.private_key = self.miner.private_key, None
        while not self.difficulty_valid():
            self.nonce += 1
            print(self.hash())
        self.miner.private_key = private_key

    def to_json(self):
        assert self.miner.private_key is None, 'You are trying to jsonify with a private key'
        return json.dumps(todict(self), sort_keys=True).encode()


def block_from_json(block_json):
    return Block(prev_hash=block_json['prev_hash'],
                 time=block_json['time'],
                 transactions=block_json['transactions'],
                 miner=user_from_json(block_json['miner']),
                 nonce=block_json['nonce'],
                 signature=block_json['signature'])


@dataclass
class Blockchain:
    chain: List[Block] = Block()

    def is_valid(self):
        """
        :return: if all the blocks are valid
                and the hash pointers are correct
        """
        prev_block = self.chain[0]
        for block in self.chain[1:]:
            if not block.is_valid():
                return False
            if prev_block.hash(for_mining=False) != block.prev_hash:
                return False
            prev_block = block
        return True

    def to_json(self):
        return json.dumps(todict(self), sort_keys=True).encode()


def blockchain_from_json(blockchain_json):
    """
    :param blockchain_json: jsonified blockchain object
    :return: Blockchain object
    """
    return Blockchain(chain=json.loads(blockchain_json['chain']))
