from hashlib import sha256
import json
import time
from datetime import datetime
import requests
# class to define block propertities
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
    # function to compute block hash 
    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    # difficulty of hash algorithm
    difficulty = 2

    def __init__(self):
        # property that will hold un confirmed transaction
        self.unconfirmed_transactions = []
        # property that will hold mined / confirmed transactions after mining
        self.chain = []

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    # return last block from chain
    @property
    def last_block(self):
        return self.chain[-1]

    # return block at given index
    def block_at_index(self, index):
        return self.chain[index]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    # add transaction / block in unconfirmed transactions
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    # verify that all blocks in chain has valid hash
    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        return True

class BlockchainManager:
    
    def __init__(self, peers):
        self.peers = list(peers)
        self.blockchain = Blockchain()

    # this method will be called from initialize_components in main.py
    # if there is any available peer then chain parameter will contain the copy of blockchain
    # if there is no peer available then peer will have value as None so we will create genesis block
    def initialize(self, chain):
        if(chain is None):
            print('There is no peer available, genesis block created.')
            self.blockchain.create_genesis_block()
        else:
            for block_data in chain:
                block = Block(block_data["index"],
                block_data["transactions"],
                block_data["timestamp"],
                block_data["previous_hash"],
                block_data["nonce"])
                block.hash=block.compute_hash()
                self.blockchain.chain.append(block)
                
    # function to find block on given index
    def findblock(self, index):
        index = int(index)
        if index > len(self.blockchain.chain)-1 or index < 0:
            print('block not found')
            return None
        block = self.blockchain.block_at_index(index)
        return json.loads(block.transactions[0])

    # function to ask block number from user and find it in blockchain
    def readblock(self):
        blockNo = ''
        while len(blockNo) == 0:
            blockNo = input("Please enter block number: ")
        
        return (blockNo, self.findblock(blockNo))

    # function to store data (pointer and metadata) on blockchain
    def new_transaction(self, pointer, user_id, privacy_type, client_name):
        dataObj = {
            'data':pointer,
            'meta-data' : {
                'user-id':user_id,
                'data-entry-date':datetime.now().strftime("%d/%m/%Y"),
                'data-entry-time':datetime.now().strftime("%H:%M:%S"),
                'privacy-type':privacy_type,
                'client-name':client_name
            }
        }
        # create json string
        jsonStr = json.dumps(dataObj)
        self.blockchain.add_new_transaction(jsonStr)

    # check all peers that are currently active
    def consensus(self):
        """
        Our naive consnsus algorithm. If a longer valid chain is
        found, our chain is replaced with it.
        """
        longest_chain = None
        current_len = len(self.blockchain.chain)
        # not responding peers to remove
        remove_peers = []
        for peer in self.peers:
            try:
                response = requests.get(peer['client_address']+'/chain')
                chain = response.json()
                length = len(chain)
                if length > current_len and self.blockchain.check_chain_validity(chain):
                    current_len = length
                    longest_chain = chain
            except:
                remove_peers.append(peer)
        
        # remove not responding peers from main list
        for peer in remove_peers:
            self.peers.remove(peer)
        
        if longest_chain:
            self.initialize(longest_chain)
            return True

        return False

    def mine_unconfirmed_transactions(self):
        result = self.blockchain.mine()
        if not result:
            return "No transactions to mine"
        else:
            # Making sure we have the longest chain before announcing to the network
            chain_length = len(self.blockchain.chain)
            self.consensus()
            print('consensus method called')
            if chain_length == len(self.blockchain.chain):
                # announce the recently mined block to the network
                self.announce_new_block(self.blockchain.last_block)
                print("Block #{} is announced to network.".format(self.blockchain.last_block.index))
            return "Block #{} is mined.".format(self.blockchain.last_block.index)

    # replicate block to all active peers
    def announce_new_block(self, block):
        """
        A function to announce to the network once a block has been mined.
        Other blocks can simply verify the proof of work and add it to their
        respective chains.
        """
        for peer in self.peers:
            url = peer['client_address']+"/chain"
            try:
                headers = {'Content-Type': "application/json"}
                requests.post(url,
                            data=json.dumps(block.__dict__, sort_keys=True),
                            headers=headers)
                print(url+' -> block added')
            except:
                print(url+' -> block failed')