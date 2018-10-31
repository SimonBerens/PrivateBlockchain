# PrivateBlockchain

## What is this?
This is a python implementation of a private blockchain. In this blockchain, you can securely send cryptocurrency 
to an approved list of users.

## How does it work?
The owner of the bootnode/network will generate a list of hashed IDs, and a corresponding list of unhashed IDs.
To each user, the owner will send the list of hashed IDs, and only that user's unhashed ID. This way, only someone who
has a valid unhashed ID that corresponds to a hashed ID in the users will be able to join the network. These users are
(as of v0) all full nodes. 

Users are identified with their public key, which they announce when they claim their hashed ID. In v0, there is no
automated way to add users because there is no way to tell if they are legitimate or not. The only way to add a user is 
through manual consensus, where everyone adds the user to their users.json.

Transactions store a User sender and recipient, who must be in the list of users. The sender is to specify a reward for
for the miner to include the transaction in their block. The block is verified using the public key of the user.

Blocks store a list of transactions. There is no coinbase transaction that goes into the block for mining it, rather,
the mining reward is added automatically when calculating the balance of a user. The same applies for the sum of the
transaction rewards. A block is verified by the public key of the miner. A block is mined automatically when certain
properties are met, for example the sum of the transaction fees.

## Design Decisions
In the making of this blockchain, I had the choice of either relying on a predistributed set of public/private keys,
or a predistributed list of hashed ID's that would could be claimed and then associated with the public key provided by
the claimer. I chose to go with predistributed IDs because if the distributor were to be hacked, if the ID was claimed
nothing bad would happen, but in the case of predistributed keys the hacker would have effective control of your account 
regardless of whether or not it was claimed.

I chose not to add coinbase transactions and rather to compute them directly because then you have to verify them.

Keys are used in their raw form (with \n's visible) for clarity

There is an html interface for ease of the user. However, because other people can access it as well I could not allow
for items such as private keys unhashed ids be preloaded. The interface uses flask Sessions so you don't need to
constantly access me.json, and so other people can still use the blockchain if they do not have access to their server,
but it is not recommended to claim users and submit transactions on other people's servers as they may be running
malicious code that takes your unhashed id and private key.

## Setup
1. Clone this project onto a server that is running python 3.7 or above
2. In the project repo, pip install -r requirements.txt
3. Run createfiles.py, which will create a me.json, nodes.json, and users.json file
4. If you have a preexisting list of users and/or nodes, place them into the users.json and/or nodes.json files respectively
5. In config.py, change the url and port to the url and port of the server
6. Run run.py from the project directory
7. Pull the most recent list of users and nodes from the bootnode
8. Using your predetermined unhashed ID and the generated keys in me.json claim your user

