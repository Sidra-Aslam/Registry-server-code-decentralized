from flask import Flask, request, jsonify
from argparse import ArgumentParser
import json
import requests
import threading
from blockchain_manager import BlockchainManager, Block
from encryption_manager import EncryptionManager
from rbac_manager import RbacManager
from dht_manager import DhtManager
from kademlia.utils import digest
import asyncio
from urllib.parse import urlparse
from time import sleep
import hashlib
import uuid

# variable to store perrs list
peer_list = None
# blockchain manager object
blockChainManager = None

# encryption manager object
encryptionManager = None

# rbac manager object
rbac = RbacManager()

# name of current client
client_name = None

# name of current client
client_role = None

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

# shared messages
messages = []

# create flask app object
app = Flask(__name__)

# api to receive block number of shared data
# this will be called from any other client after sharing data
@app.route('/shared_data', methods=['POST'])
def shared_data():
    global messages
    # receive message
    msg = request.data.decode('utf-8')
    print(msg)
    messages.append(msg)
    return '', 200

# api to return public key
# this will be called from any other client
@app.route('/public_key', methods=['GET'])
def public_key():
    global encryptionManager
    return encryptionManager.public_key

# api to update whole peer list, this will be called by registry server
@app.route('/peers', methods=['POST'])
def peers():
    global peer_list
    global blockChainManager
    peer_list = list(request.get_json())
    # remove my endpoint from peer list
    peer_list = [p for p in peer_list if p['client_address'] != my_endpoint]

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
            {"client_address": my_endpoint, "client_name": client_name}), headers=headers)
        if(req.ok):
            print('Connected with registry server')
        else:
            print('Failed to connect with registry server.')
            exit()            
    except:
        print('Failed to connect with registry server.')
        exit()

# function to disconnect with registry server
def unregister():
    headers = {'Content-Type': "application/json"}
    requests.post(registry_server+ "/peers", data=json.dumps(
        {"client_address": my_endpoint, "client_name": client_name}), headers=headers)         

# initialize blockchain copy
def initialize_blockchain():
    global blockChainManager
    global peer_list
    blockChainManager = BlockchainManager(peer_list)
    chain_initializer = None
    headers = {'Content-Type': "application/json"}
    for peer in peer_list:
        try:
            response = requests.get(peer['client_address']+ "/chain", headers=headers)
            if(response.ok):
                # get blockchain copy in json format
                chain_initializer=response.json()
                print('blockchain copy received from ' + peer['client_address'])
            
            # if BC copy received then do not try to receive block chain copy from other clients
            break
        except:
            print(peer['client_address']+' not responding, trying next peer to fetch blockchain copy')

    # initialize blockchain copy on blockhcain manager object 
    blockChainManager.initialize(chain_initializer)

# main component initializer
def initialize_components():
    register()
    initialize_blockchain()

# data input function for transporter actor
def transporter_data_input(block=None):
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

    data = json.dumps(data)
    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        # encrypt data with public key
        ecrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)

        create_data(ecrypted_data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# data input function for wood_cutter actor
def wood_cutter_data_input(block=None):
    # wood_cutter object to hold private data
    private_data = {'UserId': '', 'ProductId': '', 'Location': '', }
    # wood_cutter object to hold sensitive data
    sensitive_data = {'DateOfCutting': ''}
    # wood_cutter object to hold public data
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

    data = json.dumps(data)
    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        # encrypt data with public key
        ecrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)

        create_data(ecrypted_data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# data input function for warehouse_storage actor
def warehouse_storage_data_input(block=None):
    # wood_cutter object to hold private data
    private_data = {'UserId': '', 'ProductId': '', 'ProductStorageLocation': '', 'ProcessedDateTime':'', }
    # wood_cutter object to hold sensitive data
    sensitive_data = {'FreeStorageSpace': '', 'Quantity':''}
    # wood_cutter object to hold public data
    public_data = {'Processed': ''}
    
    # take private data from actor
    while len(private_data['UserId']) == 0:
        private_data['UserId'] = input("User Id: ")
    while len(private_data['ProductId']) == 0:
        private_data['ProductId'] = input("Product Id: ")
    while len(private_data['ProductStorageLocation']) == 0:
        private_data['ProductStorageLocation'] = input("Product storage location: ")
    while len(private_data['ProcessedDateTime']) == 0:
        private_data['ProcessedDateTime'] = input("Processed date and time: ")
    
    # take private data from actor
    while len(sensitive_data['FreeStorageSpace']) == 0:
        sensitive_data['FreeStorageSpace'] = input("Free storage space: ")
    while len(sensitive_data['Quantity']) == 0:
        sensitive_data['Quantity'] = input("Quantity: ")
    
    # take other data from actor
    while len(public_data['Processed']) == 0:
        public_data['Processed'] = input("Processed (Yes/No): ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    data = json.dumps(data)
    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        # encrypt data with public key
        ecrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)

        create_data(ecrypted_data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# data input function for furniture_assembly actor
def furniture_assembly_data_input(block=None):
    # wood_cutter object to hold private data
    private_data = {'UserId': '', 'FurnitureId': ''}
    # wood_cutter object to hold sensitive data
    sensitive_data = {'NumberOfPieces': '', 'FurnitureDesign':'' }
    # wood_cutter object to hold public data
    public_data = {'FurnitureName': ''}
    
    # take private data from actor
    while len(private_data['UserId']) == 0:
        private_data['UserId'] = input("User Id: ")
    while len(private_data['FurnitureId']) == 0:
        private_data['FurnitureId'] = input("Furniture Id: ")
    
    # take private data from actor
    while len(sensitive_data['NumberOfPieces']) == 0:
        sensitive_data['NumberOfPieces'] = input("Number of pieces (3 furniture sets): ")
    while len(sensitive_data['FurnitureDesign']) == 0:
        sensitive_data['FurnitureDesign'] = input("Furniture Design: ")
    
    # take other data from actor
    while len(public_data['FurnitureName']) == 0:
        public_data['FurnitureName'] = input("Furniture Name: ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    data = json.dumps(data)
    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        # encrypt data with public key
        ecrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)

        create_data(ecrypted_data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# data input function for furniture_assembly actor
def furniture_shop_data_input(block=None):
    # wood_cutter object to hold private data
    private_data = {'UserId': ''}
    # wood_cutter object to hold sensitive data
    sensitive_data = {'FurnitureShopLocation': '', 'PurchasedDateAndTime':'' }
    # wood_cutter object to hold public data
    public_data = {'FurnitureQuality': ''}
    
    # take private data from actor
    while len(private_data['UserId']) == 0:
        private_data['UserId'] = input("User Id: ")
    
    # take private data from actor
    while len(sensitive_data['FurnitureShopLocation']) == 0:
        sensitive_data['FurnitureShopLocation'] = input("Furniture shop location: ")
    while len(sensitive_data['PurchasedDateAndTime']) == 0:
        sensitive_data['PurchasedDateAndTime'] = input("Purchased date and time: ")
    
    # take other data from actor
    while len(public_data['FurnitureQuality']) == 0:
        public_data['FurnitureQuality'] = input("Furniture quality: ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    data = json.dumps(data)
    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        # encrypt data with public key
        ecrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)

        create_data(ecrypted_data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# data input function for customer actor
def customer_data_input(block=None):
    # wood_cutter object to hold private data
    private_data = {'UserId': '', 'ProductId': '', 'PaymentDetails': '', }
    # wood_cutter object to hold sensitive data
    sensitive_data = {'PurchasedDateAndTime': '', 'PurchasedQuantity':'', 'Style':''}
    # wood_cutter object to hold public data
    public_data = {}
    
    # take private data from actor
    while len(private_data['UserId']) == 0:
        private_data['UserId'] = input("User Id: ")
    while len(private_data['ProductId']) == 0:
        private_data['ProductId'] = input("Product Id: ")
    while len(private_data['PaymentDetails']) == 0:
        private_data['PaymentDetails'] = input("Payment details: ")
    
    # take private data from actor
    while len(sensitive_data['PurchasedDateAndTime']) == 0:
        sensitive_data['PurchasedDateAndTime'] = input("Purchased date and time: ")
    while len(sensitive_data['PurchasedQuantity']) == 0:
        sensitive_data['PurchasedQuantity'] = input("Purchased quantity: ")
    while len(sensitive_data['Style']) == 0:
        sensitive_data['Style'] = input("Style: ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    data = json.dumps(data)
    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        # encrypt data with public key
        ecrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)

        create_data(ecrypted_data, private_data['UserId'], 'private-data')
    else:
        update_data(data, block)

# store data method
# pointer and meta data will be stored on blockchain
# actual data will be stored on dht
def create_data(ecrypted_data, user_id, privacy_type):
    # generate hash b using kademlia digest built-in function, which uses SHA1 algorithm to generate hash
    pointer = digest(ecrypted_data).hex()

    # store data on dht node
    dht_manager.set_value(pointer, ecrypted_data)
    
    # store pointer and meta data on blockchain (transaction will be added to unconfirmed list)
    blockChainManager.new_transaction(pointer, user_id, privacy_type)

    # mine unconfirmed transactions and announce block to all peers
    result = blockChainManager.mine_unconfirmed_transactions()
    print(result)
    return result

# read data 
# this function will return block
def read_data():
    blockNo = ''
    while len(blockNo) == 0:
        blockNo = input("Please enter block number to display: ")
    
    # find block
    block = blockChainManager.findblock(blockNo)
    if(block is not None):
        data = decrypt_block_content(block)
        
        if data is not None:
            print(data)
            return block
        else:
            return None
    else:
        print('block not found')
        return None

def update_data(data, block):
    # extract pointer from existing block
    pointer = block['data']

    # encrypt data with public key
    ecrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)
    # store data on dht node
    dht_manager.set_value(pointer, ecrypted_data)
    
    print('data updated')

def delete_data(block):
    # extract pointer from existing block
    pointer = json.loads(block.transactions[0])['data']
    # 'DELETED' will identify that data is deleted
    dht_manager.set_value(pointer, 'DELETED')
    print('Data deleted on DHT.')

def decrypt_block_content(block):
    if(block is not None):
        # extract pointer from block object
        pointer = block['data']
        # read metadata from block
        meta_data = block['meta-data']
    
        # get block privacy type e.g private, sensitive or public
        privacy_type = meta_data['privacy-type']
        
        # retrieve data from dht against provided pointer
        dht_data = dht_manager.get_value(pointer)

        # check if current role is valid to access block based on privacy type
        if( (client_role == 'owner') or
            (privacy_type == 'sensitive-data' and client_role == 'business_partner') or
            (privacy_type == 'public-data' and client_role == 'public_user')):
            print('Privacy validated')
        else:
            print('You can not access this data.')
            return None

        # check if dht_data is deleted then retun None
        if(dht_data == 'DELETED'):
            print('DHT data is deleted.')
            return None

        elif dht_data is not None:
            # convert to json (public and sensitive data)
            if(privacy_type != 'private-data'):
                dht_data = json.loads(dht_data)
            
            if(privacy_type == 'private-data'):
                # decrypt dht data with owner's private key
                decrypted_data = encryptionManager.decrypt(dht_data, encryptionManager.private_key)
                print("Data is decrypted using owner's private key")


            # if data is encrypted with public key then decrypt data with receiver's private key
            elif('asymetric-data' in dht_data):
                # decrypt asymetric data by using receiver's private key
                decrypted_data = encryptionManager.decrypt(dht_data['asymetric-data'], encryptionManager.private_key)
                print("Data is decrypted using receivers's private key")


            if decrypted_data is not None:
                return decrypted_data
            else:
                return None

    else:
        print('block not found')
        return None

# get public key of receiver using endpoing '/public_key'
def get_key(client):
    try:
        # get one peer endpoint from peer_list
        peer = [p for p in peer_list if p['client_name'] == client]
        if len(peer) > 0:
            response = requests.get(peer[0]['client_address']+ "/public_key")
            if response.ok:
                return response.text
            else:
                return None
        else:
            print(client + ' peer is offline.')
            return None
    except:
        print(client + ' peer is offline.')
        return None

# call '/shared_data' endpoint of receiver to share data
def send_message(client, message):
    try:
        # find peer from peer_list
        peer = [p for p in peer_list if p['client_name'] == client]
        if len(peer) > 0:
            # send shared data block number to receiver
            requests.post(peer[0]['client_address']+ "/shared_data", data=message)
        else:
            print(client + ' peer is offline.')
    except:
        print('Failed to send message')

# this method will be used to share data with other actors and roles
def share_data(blockNo, shareWithClients, shareWithRoles):
    # find block from blockchain by block no
    block = blockChainManager.findblock(blockNo)

    # access meta data from block
    meta_data = block['meta-data']
    
    # get block privacy type e.g private, sensitive or public from this metadata
    privacy_type = meta_data['privacy-type']

    if(privacy_type != 'private-data'):
        print('This block is already shared, it can not be shared again.')
        return None
        
    # decrypt block
    data = decrypt_block_content(block)
    
    # check if data is not deleted
    if(data is not None):
        # read user id from private data
        user_id = data['private']['UserId']
        # clients with whom data will be shared
        clients = shareWithClients.split(',')
        
        if(shareWithRoles == 'business_partner'):
            # there is one actor then use public key encryption
            if(len(clients) == 1):
                # there is only one actor
                receiver_name = clients[0]
                # retrieve receivers public key using endpoint ''
                receiver_public_key = get_key(receiver_name)
                
                # encrypt sensitive data with receiver's public key
                encrypted_text = encryptionManager.encrypt(data['sensitive'], receiver_public_key)
                print("Data is encrypted using receiver's public key")

                # create object which will contain encrypted text
                data = json.dumps({'asymetric-data': encrypted_text})

                # store data with privacy type as 'sensitive-data'. e.g block 2 is mined
                blockNo = create_data(data, user_id, 'sensitive-data')
                
                # send block number to receiver through enndpoint, eng block 2 is mined
                send_message(receiver_name, blockNo)

        elif(shareWithRoles == 'public_user'):
            # there is one actor then use public key encryption
            if(len(clients) == 1):
                # there is only one actor
                receiver_name = clients[0]
                receiver_public_key = get_key(receiver_name)
                
                # encrypt public data
                encrypted_text = encryptionManager.encrypt(data['public'], receiver_public_key)
                print("Data is encrypted using receiver's public key")

                # create object which will contain encrypted text
                data = json.dumps({'asymetric-data': encrypted_text})

                # store data with privacy type as 'public-data'
                blockNo = create_data(data, user_id, 'public-data')
                
                # send block number to receiver
                send_message(receiver_name, blockNo)

def display_menu():
    def print_menu():
        print(30 * "-", client_name, " - ", client_role, 30 * "-")
        print("1. Create data ")
        print("2. Read data ")
        print("3. Update data ")
        print("4. Delete data ")
        print("5. Share Data ")
        print("6. Display Messages ")
        print("7. Display peers ")
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
            # verify permission
            if(rbac.verify_permission(client_role, 'write', 'blockchain')):
                # display menu based on actor name
                if(client_name == 'wood_cutter'):
                    wood_cutter_data_input()
                elif(client_name == 'transporter'):
                    transporter_data_input()
                elif(client_name == 'warehouse_storage'):
                    warehouse_storage_data_input()
                elif(client_name == 'furniture_assembly'):
                    furniture_assembly_data_input()
                elif(client_name == 'furniture_shop'):
                    furniture_shop_data_input()
                elif(client_name == 'customer'):
                    customer_data_input()    
            else:
                print('You are not authorized to perform this action.')
            
            loop = True
        elif choice == '2':
            # read data
             # verify permission
            if(rbac.verify_permission(client_role, 'read', 'blockchain')):
                read_data()
            else:
                print('You are not authorized to perform this action.')
            
            loop = True
        elif choice == '3':
            # update data
            # verify permission
            if(rbac.verify_permission(client_role, 'update', 'blockchain')):
                # read block
                block = read_data()
                # if block found then take new input from user to update data
                if(block is not None):
                    if(client_name == 'wood_cutter'):
                        wood_cutter_data_input(block)
                    elif(client_name == 'transporter'):
                        transporter_data_input(block)
                    elif(client_name == 'warehouse_storage'):
                        warehouse_storage_data_input(block)
                    elif(client_name == 'furniture_assembly'):
                        furniture_assembly_data_input(block)
                    elif(client_name == 'furniture_shop'):
                        furniture_shop_data_input(block)
                    elif(client_name == 'customer'):
                        customer_data_input(block)
            else:
                print('You are not authorized to perform this action.')
            
            loop = True

        elif choice == '4':
            # delete data
             # verify permission
            if(rbac.verify_permission(client_role, 'delete', 'blockchain')):
                # read block
                block = read_data()
                if(block is not None):
                    delete_data(block)        
            else:
                print('You are not authorized to perform this action.')
            
                loop = True
        elif choice == '5':
            # share data
            # verify permission
            if(rbac.verify_permission(client_role, 'share', 'blockchain')):
                blockNo = ''
                shareWithActors = ''
                shareWithRoles = ''
                while len(blockNo) == 0:
                    blockNo = input("Enter block# to share: ")
                while len(shareWithActors) == 0:
                    shareWithActors = input(
                        "Write actor names you want to share data (i.e {0}): ".format(rbac.client_names))
                while len(shareWithRoles) == 0:
                    shareWithRoles = input(
                        "Do you want to share data with business_partner or public_user ?")
                
                # share data to users
                share_data(blockNo, shareWithActors, shareWithRoles)
            else:
                print('You are not authorized to perform this action.')
            loop = True

        elif choice == '6':
            # display message
            print(messages)
            loop=True
        elif choice == '7':
            # display available peers
            print(peer_list)
            loop=True
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
    parser.add_argument('-c', '--client', default='wood_cutter', help='Enter client name')
    parser.add_argument('-r', '--role', default='business_partner', help='Enter role name')
    
    args = parser.parse_args()
    port = args.port
    client_name = args.client
    client_role = args.role
    # authenticate client name and role using rabac manager
    if(not rbac.authenticate(client_name, client_role)):
        print('Not authenticated.')
        exit()
    
    encryptionManager = EncryptionManager()

    registry_server = "http://127.0.0.1:8080/"
    my_endpoint = "http://127.0.0.1:"+str(port)
    print("Registry Server Url: "+registry_server)
    my_dht_node_endpoint = ('127.0.0.1', port+1)

    # start new thread for flask http api
    apiThread = threading.Thread(target=app.run, kwargs={'host':'127.0.0.1', 'port': port, 'debug': False})
    apiThread.daemon=True
    apiThread.start()
    
    initialize_components()
  # object of dht_manager. It will start the dht node
    dht_manager = DhtManager(port+1, peer_list)

    # start new thread for dht node to continusly listen
    dhtThread = threading.Thread(target=dht_manager.start_node)
    dhtThread.daemon=True
    dhtThread.start()
    print('DHT node running on port: ' + str(dht_manager.port))
    # wait for at least four seconds till api and dht node get started 
    sleep(2)
    # display menu
    display_menu()