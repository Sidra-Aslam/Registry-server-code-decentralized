import logging
from flask import Flask, request, jsonify
from argparse import ArgumentParser
import json
import requests
import threading
from blockchain_manager import BlockchainManager, Block
from dht_manager import DhtManager
from kademlia.network import Server, Node
import asyncio
from urllib.parse import urlparse
from time import sleep
import hashlib
import uuid

# variable to store perrs list
peer_list = set()
# blockchain manager object
blockChainManager = None

# name of current client
client_name = None

# port at which client api is running
port = None

# url on which registry server is running
registry_server = None

# api url on which current program is running
my_endpoint = None

# current dht node address
my_dht_node_endpoint = None

# dht manage object to access current dht node
dht_manager = None
# create flask app object
app = Flask(__name__)

# api to update whole peer list, this will be called by registry server
@app.route('/peers', methods=['POST'])
def peers():
    global peer_list
    global blockChainManager
    peer_list = set(request.get_json())
    peer_list.remove(my_endpoint)
    if(blockChainManager is not None):
        blockChainManager.peers = peer_list
    print('Peer list updated')
    print(peer_list)
    return ('', 200)

# api to return blockchain copy
# this will be called from any other client
@app.route('/chain', methods=['GET'])
def chain():
    global blockChainManager
    chain_data = []
    # iterate all blocks from blockchain
    for block in blockChainManager.blockchain.chain:
        chain_data.append(block.__dict__)
    
    return jsonify(chain_data)

# endpoint to add blocks, this will be called by other clients and replicate data on other BC nodes after mining
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    # create new block object
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    # add block to the chain
    added = blockChainManager.blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201

# function to connect with registry server
def register():
    try:
        headers = {'Content-Type': "application/json"}
        req = requests.post(registry_server+ "/peers", data=json.dumps(
            {"client_address": my_endpoint}), headers=headers)
        if(req.ok):
            print('Connected with registry server')
        else:
            print('Failed to connect with registry server.')
            exit()            
    except Exception as e:
        print('Failed to connect with registry server.')
        exit()

# function to disconnect with registry server
def unregister():
    headers = {'Content-Type': "application/json"}
    requests.post(registry_server+ "/peers", data=json.dumps(
        {"client_address": my_endpoint}), headers=headers)         

# initialize blockchain copy
def initialize_blockchain():
    global blockChainManager
    global peer_list
    blockChainManager = BlockchainManager(peer_list)
    chain_initializer = None
    headers = {'Content-Type': "application/json"}
    for peer in peer_list:
        if peer != my_endpoint:
            try:
                response = requests.get(peer+ "/chain", headers=headers)
                if(response.ok):
                    # get blockchain copy in json format
                    chain_initializer=response.json()
                    print('blockchain copy received from ' + peer)
                
                # if BC copy received then do not try to receive block chain copy from other clients
                break
            except Exception as e:
                print(peer+' not responding, trying next peer to fetch blockchain copy')
    
    # initialize blockchain copy on blockhcain manager object 
    blockChainManager.initialize(chain_initializer)

# main component initializer
def initialize_components():
    register()
    initialize_blockchain()

# start dht node for current client
def start_dht_node():
    global dht_manager

    # variable to store other node addresses
    dht_other_nodes = []
    # iterate all available peers
    for peer in peer_list:
        endpoint = urlparse(peer)
        # append dht host and port number of other node to dht_other_nodes variable
        dht_other_nodes.append((endpoint.hostname, endpoint.port+1))

    # to display log information
    log = logging.getLogger('kademlia')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(True)

    # create dht node object
    dht_node = Server()
    # start node on port + 1
    loop.run_until_complete(dht_node.listen(port+1))

    # create dht manager object for current node
    dht_manager = DhtManager(my_dht_node_endpoint)

    # if there is any existing dht node then connect current node to all other nodes
    if(len(dht_other_nodes) > 0):
        # connect with other dht nodes
        loop.run_until_complete(dht_node.bootstrap(dht_other_nodes))
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        dht_node.stop()
        loop.close()

# data input function for transport actor
def transport_data_input(block=None):
    # tranpsort actor data object to hold private data
    private_data = {'UserId': '', 'ProductId': '', 'PickupPlace': ''}
    # tranpsort actor data object to hold sensitive data
    sensitive_data = {'DeliveryPlace': '', 'PickupDate': ''}
    # tranpsort actor data object to hold public data
    public_data = {'DeliveryDate': ''}

    # take private data from actor
    while len(private_data['UserId']) == 0:
        private_data['UserId'] = input("User Id: ")
    while len(private_data['ProductId']) == 0:
        private_data['ProductId'] = input("Product Id: ")
    while len(private_data['PickupPlace']) == 0:
        private_data['PickupPlace'] = input("Pickup place: ")

    # take privacy sensitive data from actor
    while len(sensitive_data['DeliveryPlace']) == 0:
        sensitive_data['DeliveryPlace'] = input("Delivery place: ")
    while len(sensitive_data['PickupDate']) == 0:
        sensitive_data['PickupDate'] = input("Pickup date: ")

    # take public data from actor
    while len(public_data['DeliveryDate']) == 0:
        public_data['DeliveryDate'] = input("Delivery date: ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        create_data(data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# data input function for woodcutting actor
def woodcutting_data_input(block=None):
    # woodcutting object to hold private data
    private_data = {'UserId': '', 'ProductId': '', 'Location': '', }
    # woodcutting object to hold sensitive data
    sensitive_data = {'DateOfCutting': ''}
    # woodcutting object to hold public data
    public_data = {'WoodType': ''}
    
    # take private data from actor
    while len(private_data['UserId']) == 0:
        private_data['UserId'] = input("User Id: ")
    while len(private_data['ProductId']) == 0:
        private_data['ProductId'] = input("Product Id: ")
    while len(private_data['Location']) == 0:
        private_data['Location'] = input("Location: ")
    
    # take private data from actor
    while len(sensitive_data['DateOfCutting']) == 0:
        sensitive_data['DateOfCutting'] = input("Date of cutting: ")

    # take other data from actor
    while len(public_data['WoodType']) == 0:
        public_data['WoodType'] = input("Wood Type: ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    if(block is None):
        create_data(data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# generate hash from data
def generate_hash(data):
    if not isinstance(data, bytes):
        string = str(data).encode('utf8')
    return hashlib.sha256(string).digest().hex()

# store data method
# pointer and meta data will be stored on blockchain
# actual data will be stored on dht
def create_data(data, user_id, privacy_type):
    # return hash of data
    pointer = generate_hash(data) 
    data = json.dumps(data)

    # store data on dht node
    asyncio.run(dht_manager.set_value(pointer, data))
    
    # store pointer and meta data on blockchain (transaction will be added to unconfirmed list)
    blockChainManager.new_transaction(pointer, user_id, privacy_type)

    # mine unconfirmed transactions and announce block to all peers
    result = blockChainManager.mine_unconfirmed_transactions()
    print(result)

# read data
def read_data():
    blockNo = ''
    while len(blockNo) == 0:
        blockNo = input("Please enter block number to display: ")
    # find block
    block = blockChainManager.findblock(blockNo)
    if(block is not None):
        print(block.__dict__)
        # extract pointer from block object
        pointer = json.loads(block.transactions[0])['data']
        # retrieve data from dht against provided pointer
        dht_data = asyncio.run(dht_manager.get_value(pointer))
        print(dht_data)
    else:
        print('block not found')

def update_data(data, block):
    pass

def delete_data():
    pass

def share_data():
    pass

def display_menu():
    def print_menu():
        print(30 * "-", client_name, 30 * "-")
        print("1. Create data ")
        print("2. Read data ")
        print("3. Update data ")
        print("4. Delete data ")
        print("5. Share Data ")
        print("6. Send Message ")
        print("7. Receive Message ")
        print("8. Display peers ")
        print("0. Exit ")
        print(73 * "-")

    loop = True
    # While loop which will keep going until loop = False
    while loop:
        print_menu()    # Displays menu
        # user choise to select specific menu
        choice = input("Enter your choice [1-7]: ")

        if choice == '1':
            # create data
            # display menu based on actor name
            if(client_name == 'wood_cutting'):
                woodcutting_data_input()
            elif(client_name == 'transport'):
                transport_data_input()

            loop = True
        elif choice == '2':
            # read data
            read_data()

            loop = True
        elif choice == '3':
            # update data
            # TODO
            pass
        elif choice == '4':
            # delete data
            # TODO
            pass
        elif choice == '5':
            # share data
            #TODO
            pass
        elif choice == '6':
            # send message
            # TODO
            pass
        elif choice == '7':
            # read message
            # TODO
            pass
        elif choice == '8':
            # display available peers
            print(peer_list)
        elif choice == '0':
            unregister()
            print("Exiting..")
            loop = False  # This will make the while loop to end
        else:
            # Any inputs other than values 1-7 we print an error message
            input("Wrong menu selection. Enter any key to try again..")
    return [choice]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8090, type=int, help='port to listen on')
    parser.add_argument('-c', '--client', default='wood_cutting', help='Enter client name')
    args = parser.parse_args()
    port = args.port
    client_name = args.client

    registry_server = "http://127.0.0.1:8080/"
    my_endpoint = "http://127.0.0.1:"+str(port)
    print("Registry Server Url: "+registry_server)
    my_dht_node_endpoint = ('127.0.0.1', port+1)

    # start new thread for flask http api
    apiThread = threading.Thread(target=app.run, kwargs={'host':'127.0.0.1', 'port': port, 'debug': False})
    apiThread.daemon=True
    apiThread.start()
    
    initialize_components()
    
    # start new thread for dht node
    dhtThread = threading.Thread(target=start_dht_node)
    dhtThread.daemon=True
    dhtThread.start()
    # wait for at least four seconds till api and dht node get started 
    sleep(4)
    # display menu
    display_menu()