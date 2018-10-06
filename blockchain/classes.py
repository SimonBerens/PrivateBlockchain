import json
from dataclasses import dataclass
from time import time
from datetime import datetime
from Cryptodome.Signature import pkcs1_15
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA3_512
from typing import List
from copy import deepcopy
from config import DIFFICULTY, TRANSACTION_MIN_VALUE, NUM_KEY_BITS


def check_valid_type(obj, *args):
    if len(args) == 0:
        args = ['User', 'Transaction', 'Block', 'Blockchain', 'TransactionMessage', 'BlockMessage']
    return type(obj).__name__ in list(args)


def to_dict(obj):
    """
    Recursively goes through fields and adds them to dictionary
    Requires for object to be one of the defined classes
    """
    assert check_valid_type(obj)
    dictified = dict()
    for name, value in obj.__dict__.items():
        if check_valid_type(value):
            dictified[name] = to_dict(value)
        else:
            dictified[name] = value
    return dictified


def to_json(obj):
    return json.dumps(to_dict(obj), sort_keys=True)


def hasher(obj):
    """
    :return: SHA3_512 hasher object
    """
    assert check_valid_type(obj, 'Transaction', 'Block', 'bytes')
    return SHA3_512.new().update(obj if type(obj) == bytes else to_json(obj).encode())


@dataclass
class User:
    alias: str
    hashed_id: str
    public_key: str = None
    private_key: str = None

    def __post_init__(self):
        #  easier to do this here than in user_from_json_str
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

    def sign(self, message):
        """
        Only use for when you have the private key
        :param message: Block or Transaction to sign
        """
        assert check_valid_type(message, 'TransactionMessage', 'BlockMessage')
        assert message.signature is None, 'This Message is already signed'
        key = RSA.import_key(self.private_key)
        assert RSA.RsaKey.has_private(key), 'Invalid private key'
        signer = pkcs1_15.new(key)
        message.signature = signer.sign(hasher(message.data))

    def public_version(self):
        #  this will be used in various post-inits
        copy = deepcopy(self)
        copy.private_key = None
        return copy


def user_from_json_str(user_json_str):
    user_dict = json.loads(user_json_str)
    return User(alias=user_dict['alias'],
                hashed_id=user_dict['hashed_id'],
                public_key=user_dict['public_key'],
                private_key=user_dict['private_key'])


@dataclass
class Message:
    sender: User
    data: str
    time: str = None
    signature: str = None

    def __post_init__(self):
        self.sender = self.sender.public_version()
        if self.time is None:
            self.timestamp()

    def valid_signature(self):
        """
        :return: if the signature of the messages data is valid
        """
        public_key = RSA.import_key(self.sender.public_key)
        verifier = pkcs1_15.new(public_key)
        try:
            verifier.verify(hasher(self.data), self.signature)
        except ValueError:
            return False
        return True

    def is_valid(self):
        return self.data.is_valid() and self.valid_signature()

    def timestamp(self):
        assert self.time is None, 'This ' + str(type(self).__name__) + ' has already been timestamped'
        self.time = datetime.utcfromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


@dataclass
class Transaction:
    """
    Class for storing transactions to allow for easy verification
    """
    sender: User
    recipient: User
    value: float

    def __post_init__(self):
        self.sender = self.sender.public_version()
        self.recipient = self.recipient.public_version()

    def is_valid(self):
        return self.value <= TRANSACTION_MIN_VALUE


@dataclass
class TransactionMessage(Message):
    sender: User
    data: Transaction
    time: str = None
    signature: str = None


@dataclass
class Block:
    """
    Block class where the default constructor returns the genesis block
    """
    prev_hash: str
    miner: User
    transactions: List[TransactionMessage] = None
    nonce: int = 0

    def __post_init__(self):
        if self.transactions is None:
            self.transactions = []
        self.miner = self.miner.public_version()

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
        :return: if all the transactions are valid
                    and the hash has appropriate proof of work
        """
        return self.difficulty_valid() and self.transactions_valid()

    def mine(self):
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


@dataclass
class BlockMessage(Message):
    sender: User
    data: Block
    time: str = None
    signature: str = None


@dataclass
class Blockchain:
    chain: List[BlockMessage] = None
    transactions: List[TransactionMessage] = None

    def __post_init__(self):
        if self.chain is None:
            self.chain = []
        if self.transactions is None:
            self.transactions = []

    def genesis(self, owner):
        assert check_valid_type(owner, 'User')
        assert self.chain == [], 'This Blockchain has already been initialized'
        genesis_block = Block('00', owner)
        genesis_block.mine()
        genesis_message = BlockMessage(owner, genesis_block)
        owner.sign(genesis_message)

    def submit_transaction(self, transaction_message):
        assert check_valid_type(transaction_message, 'TransactionMessage')
        assert transaction_message.is_valid()
        self.transactions.append(transaction_message)

    def mine_transactions(self, miner):
        assert check_valid_type(miner, 'User'), 'This is not a valid miner'
        assert miner.private_key is not None, 'This User cannot sign messsages'
        prev_hash = '00' if len(self.chain) is 0 else self.chain[0].data.prev_hash
        block = Block(prev_hash, miner, self.transactions)
        block.mine()
        message = BlockMessage(miner, block)
        miner.sign(message)
        assert message.is_valid()
        self.chain.append(message)

    def is_valid(self):
        """
        :return: if all the blocks are valid
                and the hash pointers are correct
        """
        genesis = self.chain[0]
        if not genesis.is_valid():
            return False
        prev_block_message = genesis
        for block_message in self.chain[1:]:
            if not block_message.is_valid():
                return False
            if hasher(prev_block_message.data).hexdigest() != block_message.data.prev_hash:
                return False
            prev_block_message = block_message
        return True
