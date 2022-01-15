#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
from operator import truediv
from ring_manager import RingManager
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
from urllib.parse import urlparse
from time import sleep
import time
from csv_log import CSVLogger
from multiprocessing import Process
import re
from datetime import datetime


test_run = 1

data_schema = None

# variable to store perrs list
peer_list = []
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

# id of current client
client_id = None

# variable to store actors that are linked with me/my client id
my_actors_tree = []

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

# declaration of ring manager
ring_manager = None

# create flask app object
app = Flask(__name__)
# endpoint to return the data scehma of the current client/actor
@app.route('/data_schema', methods=['GET'])
def get_data_schema():
    global client_name
    # open JSON file/read JSON file
    f = open('data_schema.json',)
    # read data_schema file as an json object
    schema = json.load(f)
    # close file
    f.close()

    # return current actor's schema
    return schema[client_name]

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
    global ring_manager
    global my_actors_tree

    peer_list = list(request.get_json())
    # remove my endpoint from peer list
    peer_list = [p for p in peer_list if p['client_address'] != my_endpoint]

    if(blockChainManager is not None):
        blockChainManager.peers = peer_list

    # create object of ring manager using signer's private key and all public keys of other peers
    ring_manager = RingManager(encryptionManager.public_key, encryptionManager.private_key, peer_list)
    
    # check actors that are linked with me/my client id/within my tree to verify relation
    my_actors_tree = [p for p in peer_list if is_relation_valid(p)]
    my_actors_tree.append({"client_address": my_endpoint, "client_name": client_name, 
            "public_key": encryptionManager.public_key, "client_id":client_id})
    print('Peer list updated')
    return ('', 200)

# check if other client id is linked with me (is in same tree/hierarchy)
def is_relation_valid(other_client) -> bool:
    global client_id
    global client_name
    
    # split current client id on hyphen i.e  wood_cutting0-0
    # i.e requester is  wood_cutting1-0, in this case this is invalid company to communicate
    # because first part is mismatched with represents the company
    client_id_identifier = client_id.split('-')[0]
    if(other_client['client_name'] == client_name and other_client['client_id'].startswith(client_id_identifier) == False):
        return False
    else:
        return True

# api /chain to return blockchain copy or replicate block on peers
# this will be called from any other client
@app.route('/chain', methods=['GET', 'POST']) # route mapping with get/post request
@app.route('/chain/<actor>', methods=['POST']) # route mapping with post and block number (for request data)
def chain(actor=None):
    global blockChainManager
    global peer_list

    # return blockchain copy
    if request.method == 'GET' and actor is None:
        chain_data = []
        # iterate all blocks from blockchain
        for block in blockChainManager.blockchain.chain:
            chain_data.append(block.__dict__)
        
        return jsonify(chain_data)
    
    # for requester
    # post method with actor name so return the data after tree_verification
    elif request.method == 'POST' and actor is not None:
        # get requester role and name
        requester = request.get_json()
        # owner will verify if requester client id iis in my_actor_tree or not
        if (any(c['client_id'] == requester['client_id'] for c in my_actors_tree) == False):
            return jsonify({'error':'Invalid data request'})

        CSVLogger.timeObj['MaintainUpdateHistoryTime']=0
        # decrypt owner data
        all_data = read_my_data()
        filtered_data = []

        CSVLogger.timeObj['MetadataDateQuery'] = 0
        CSVLogger.timeObj['MetadataPropertyQuery'] = 0
        CSVLogger.timeObj['MetadataRecent'] = 0
        CSVLogger.timeObj['MetadataQueryOverallTime']=0
        if(len(all_data)>0):
            metadata_query_overalltime = time.perf_counter()
            # validate meta data query if requester has provided valid properties
            metadata_query = validate_metadata_query(requester['metadata_query'])
            filtered_data = search_metadata_query(all_data, metadata_query)
            CSVLogger.timeObj['MetadataQueryOverallTime'] = (time.perf_counter()-metadata_query_overalltime)
        
        # iterate all data/transactions
        for data in filtered_data:
            if(len(data)>1):
                # role is public user
                if requester['role'] == 'public_user':
                    data = data['public']

                # role is business partner or role is owner of other company
                # client id condition is added to handle the case when same client requests the data who has created it
                elif requester['role'] == 'business_partner' or (requester['role'] == 'owner' and requester['client_id'] != client_id):
                    # remove private data from data object
                    del data['private']
                    del data['previous_data']
                    del data['previous_pointers']
                    del data['data']
                    del data['meta-data']

        
        # current peer information, if owner read his own data
        peer = [{"client_address": my_endpoint, "client_id": client_id, 'public_key': encryptionManager.public_key}]
        
        # clinet_name is a current login user. and requester is a user who reads data
        # if data owner is not current user then look for owner endpoint from peer_list
        if client_id != requester['client_id']:
            # get one peer endpoint from peer_list to find out data requester's enspoint/ return requester's peer information 
            peer = [p for p in my_actors_tree if p['client_id'] == requester['client_id']]
        
        if len(peer) > 0:
            # extract requester's public key from peer list
            requester_public_key = peer[0]['public_key']
            print('requester client id: ' + peer[0]['client_id'])
            print('Asymmetric data encryption with requesters public key while data read request')
            # # encrypt data with requester's public key
            # encrypted_data = encryptionManager.encrypt(all_data, requester_public_key)
            
            # encrypt data with symmetric key
            encrypted_data, symmetric_key = encryptionManager.symetric_encrypt(filtered_data)
            # encrypt symmetric key with requester's public key
            encrypted_key = encryptionManager.encrypt(symmetric_key, requester_public_key)
            # create data object with symmetric data and symmetric key
            encrypted_data = json.dumps({'symmetric-data': encrypted_data, 'symmetric-key': encrypted_key})

            # create ring signature of encrypted dtaa
            sign = ring_manager.sign(encrypted_data)
            # return signature and encrypted data to requester
            return jsonify({'sign':sign,'data':encrypted_data, 'timeObj':CSVLogger.timeObj})

    # post method, this will be called by other clients to replicate data on other BC nodes after mining
    elif request.method == 'POST':
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
# algo to validate query parameters (schema_property, date, date_citeria)
def validate_metadata_query(query):
    try:
        # convert and validate query date to date and time to check is format is valid
        query['date'] = datetime.fromisoformat(query['date'])
    except:
            # if format is not valid then set empty string    
            query['date'] = ''
    
     # validate date criteria
    if query['date_criteria'] not in ('before','after','exact'):
        query['date'] = ''
        query['date_criteria'] = ''
    
    
    data_schema = get_data_schema()
    # validate schema property if it is available in data_schema file
    if(query['property'] not in data_schema['private'] and
        query['property'] not in data_schema['sensitive'] and 
        query['property'] not in data_schema['public']):
        query['property']=''
    
    return query

# apply query on all data and filter data based on the query paramertes
def search_metadata_query(all_data, query):
    filtered_data = []
    # conditions for date and date criteria
    if (query['date'] != ''):
        metadata_date_query_time=time.perf_counter()
        for data in all_data:
            # extract date and time from meta-data
            data_entry_datetime = datetime.fromisoformat(data['meta-data']['data-entry-date']+' '+data['meta-data']['data-entry-time'])

            # date criteria is exact so match the date of block and query date are same
            if(query['date_criteria'] == 'exact' and data_entry_datetime.date() == query['date'].date()):
                filtered_data.append(data)
            elif(query['date_criteria'] == 'before' and data_entry_datetime < query['date']):
                filtered_data.append(data)
            elif(query['date_criteria'] == 'after' and data_entry_datetime > query['date']):
                filtered_data.append(data)
            
        CSVLogger.timeObj['MetadataDateQuery'] = (time.perf_counter()-metadata_date_query_time)
        
    else:
        metadata_recent_query_time = time.perf_counter()
        # user have not provided any date so return last data (recent)
        filtered_data.append(all_data[-1])
        CSVLogger.timeObj['MetadataRecent'] = (time.perf_counter()-metadata_recent_query_time)

    # condition for schema property
    prop = query['property'] 
    if(prop !=''):
        metadata_property_query_time = time.perf_counter()
        filtered_properties=[]
        for data in filtered_data:
            if (prop in data['private']):
                filtered_properties.append(data['private'][prop])
            elif (prop in data['sensitive']):
                filtered_properties.append(data['sensitive'][prop])
            elif (prop in data['public']):
                filtered_properties.append(data['public'][prop])
        CSVLogger.timeObj['MetadataPropertyQuery'] = (time.perf_counter()-metadata_property_query_time)
        
        return filtered_properties
    else:
        # if user has not any scema_property then return all data (sensitive and public)
        return filtered_data

# function to connect with registry server
def register():
    try:
        headers = {'Content-Type': "application/json"}
        req = requests.post(registry_server+ "peers", data=json.dumps(
            {"client_address": my_endpoint, "client_name": client_name, 
            "public_key": encryptionManager.public_key, "client_id":client_id}), headers=headers)

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
    requests.post(registry_server+ "peers", data=json.dumps(
        {"client_address": my_endpoint, "client_name": client_name, "client_id":client_id, 
        "public_key": encryptionManager.public_key}), headers=headers)         

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
    # clear time object for each run
    CSVLogger.timeObj = {}
    # repeat the process n times
    for i in range(1):

        reg_server_start = time.perf_counter()
        register()
        CSVLogger.timeObj['RegistryServerConnectTime'] = (time.perf_counter() - reg_server_start)
        
        blockchain_start = time.perf_counter()
        initialize_blockchain()
        CSVLogger.timeObj['BlockchainCopyTime'] = (time.perf_counter() - blockchain_start)
        CSVLogger.timeObj['OverallTime'] = (time.perf_counter() - reg_server_start)
        CSVLogger.save_time()
    
    CSVLogger.initialization_csv()

# function to convert input values into json format
# value type=int,float
def format_key_value(input_text, value_type):
    try:
        # main dict object to store key value pairs
        key_values={}

        # split user input text (i.e aa:2.2,bb:44.5)
        values = input_text.split(',')
        # iterate all inputs
        for value in values:
            try:
                # split according to key value pair
                k, v=value.split(':')
                
                # strip is used to removed empty space in key or value
                k = k.strip() 
                v = v.strip()
                
                # convert value to specific type (int,float)
                if value_type=='int':
                    key_values[k]=int(v)
                elif value_type=='float':
                    key_values[k]=float(v)
                elif value_type=='text':
                    key_values[k]=v
            except:
                print('Invalid key value pair: '+value)
    except:
        print('Unable to process input values, please provide valid key value pairs and try again.')
    
    return key_values

# data input function
def data_input(block=None):
    # call get_data_schema function to return data schema
    data_schema = get_data_schema()

    # iterate private, public, sensitive data from data_schema
    for privacy_level, data in data_schema.items():
        # iterate all properties in data
        for property, value in data.items():
            # check if property value type is string
            if(isinstance(value, str)):
                # take input from user for property
                while len(data_schema[privacy_level][property]) == 0:
                    data_schema[privacy_level][property] = input('Enter '+property+': ')
            
            # check if property value type is dict object (for multiple inputs)
            elif(isinstance(value, dict)):
                print("Enter multiple inputs in format as -> key : value, ")
                while len(data_schema[privacy_level][property]) == 0:
                    # take multiple inputs (key value pairs) in comma separated format
                    input_text = input('Enter '+property+' as key value pairs (key:value,): ')
                    data_schema[privacy_level][property] = format_key_value(input_text, 'text')
            
    create_data(data_schema, block)

# store data method
# pointer and meta data will be stored on blockchain
# actual data will be stored on dht
def create_data(data, block=None):
    encryption_method = ''
    # choose encryption method
    while len(encryption_method) == 0:
        encryption_method = input("choose encryption method symmetric/asymmetric?")
    
    # repeat the process n times
    for i in range(test_run):
        # clear time object for each run
        CSVLogger.timeObj = {}
        CSVLogger.timeObj['EncDecTime'] = 0
            
        if block is not None:
            # simulate read and decryption time again
            read_my_data() # - required for test run only
            
        # verify permission again 
        rbac.verify_permission(client_role, 'write', 'blockchain') # - for test run
        
        start_time = time.perf_counter() + rbac.permission_time

        #take user id from private data
        user_id = ''
        if 'ConsumerId_private_privacy_level' in data['private']:
            user_id = data['private']['ConsumerId_private_privacy_level']
        
        encrypted_data = ''

        # if user choose asymmetric encryption option
        if(encryption_method == 'asymmetric'):
            print('Data encrypt with owners public key while creating data')
            # encrypt data with public key
            encrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)
            encrypted_data = json.dumps({'asymmetric-data': encrypted_data})

        # if user choose symmetric encryption option
        elif(encryption_method=='symmetric'):
            print('Data encrypt with symmetric key while creating data')
            # encrypt data with symmetric key
            encrypted_data, symmetric_key = encryptionManager.symetric_encrypt(data)
            print('Encrypt symmetric key with owner public key while creating data')
            # encrypt symmetric key with owner's public key
            encrypted_key = encryptionManager.encrypt(symmetric_key, encryptionManager.public_key)
            # create data object with symmetric data and symmetric key
            encrypted_data = json.dumps({'symmetric-data': encrypted_data, 'symmetric-key': encrypted_key})

        else:
            print('Invalid encryption method')
            return None

        # generate hash using kademlia digest built-in function, which uses SHA1 algorithm to generate hash
        pointer = digest(encrypted_data).hex()
        
        # store data on dht node
        dht_manager.set_value(pointer, encrypted_data)

        # blockchain start time
        bc_start_time = time.perf_counter()

        # data schema uri of current client/actor i.e http://localhost:4565/data_schema (get_data_schema)
        data_schema_uri = my_endpoint+'/data_schema'
        # store pointer and data_scema uri in the meta data on blockchain (transaction will be added to unconfirmed list)
        blockChainManager.new_transaction(pointer, user_id, client_id, data_schema_uri, block)
        
        CSVLogger.timeObj['BlockchainStorageTime'] = (time.perf_counter()-bc_start_time)
        CSVLogger.timeObj['OverallTime'] = (time.perf_counter()-start_time)+CSVLogger.timeObj['EncDecTime']
        
        print("\nTime to store pointer on blockchain without dht and decryption:", format(CSVLogger.timeObj['BlockchainStorageTime'], '.8f'))
        print("\nOverall time to create data (with encryption, dht, blockchain):", format(CSVLogger.timeObj['OverallTime'], '.8f'))
        
        print('Transaction created')
        # save time in list for current run
        CSVLogger.save_time()

    # create excel file based on encryption method
    if(encryption_method=='asymmetric'):
        CSVLogger.asym_create_data_csv()
    else:
        CSVLogger.sym_create_data_csv()

# read data 
def read_data():
    # ask actor id to read data
    actor_id = ''
    while len(actor_id) == 0:
        actor_id = input("Enter client id to request/read data: ")

    # find actor name by actor id
    actor = [p for p in my_actors_tree if p['client_id'] == actor_id]
    
    # ask metadata query parameters i.e 
    schema_property = input("Enter schema property: ")
    date = input("Enter date and time to be searched 'yyyy-mm-dd hh:mm': ")
    date_criteria=''
    if(date != ''):
        date_criteria = input("Enter date match criteria (before,after,exact): ")
    # e.g schema_propoerty such as Schedule_sensitive_privacy_level
    metadata_query = {
        'property':schema_property,
        'date':date,
        'date_criteria':date_criteria
    }

    if(len(actor) > 0):
        for i in range(test_run):
            CSVLogger.timeObj = {}
            CSVLogger.timeObj['EncDecTime'] =  0
            CSVLogger.timeObj['CreateRing'] =  0
            CSVLogger.timeObj['DhtRead'] =  0
            CSVLogger.timeObj['BlockchainReadTime'] =  0

            # simulate rbac time again 
            rbac.verify_permission(client_role, 'read', 'blockchain') # - required for test run only
            
            # calculate start time to read data 
            start_time = time.perf_counter() + rbac.permission_time
            
            # verify if the client is valid business partner
            if(rbac.check_business_partner(client_name, actor[0]['client_name'])==False):
                print('you are not business partner with '+actor[0]['client_name']+' so you can not read data.')
                return
            
            req_time = time.perf_counter()
            
            try:
                print('sending data read request to client id: '+actor[0]['client_id'])
                headers = {'Content-Type': "application/json"}
                # send data request to actor by calling /chain api+actor name
                response = requests.post(actor[0]['client_address']+ "/chain/"+actor[0]['client_name'], 
                    data=json.dumps({'role': client_role, 'client_id':client_id, 'metadata_query':metadata_query}), headers=headers)
                
                if response.ok:
                    # response object return from actor/owner
                    response_object = response.json()
                    
                    timeObj = response_object['timeObj']
                    
                    CSVLogger.timeObj['EncDecTime'] =  timeObj['EncDecTime']
                    CSVLogger.timeObj['CreateRing'] =  timeObj['CreateRing']
                    CSVLogger.timeObj['DhtRead'] =  timeObj['DhtRead']
                    CSVLogger.timeObj['BlockchainReadTime'] =  timeObj['BlockchainReadTime']
                    
                    CSVLogger.timeObj['MetadataDateQuery'] = timeObj['MetadataDateQuery']
                    CSVLogger.timeObj['MetadataPropertyQuery'] = timeObj['MetadataPropertyQuery']
                    CSVLogger.timeObj['MetadataRecent'] = timeObj['MetadataRecent']
                    CSVLogger.timeObj['MetadataQueryOverallTime'] = timeObj['MetadataQueryOverallTime']
                    CSVLogger.timeObj['MaintainUpdateHistoryTime'] = timeObj['MaintainUpdateHistoryTime']
                    
                    # verify ring signature
                    isVerified = ring_manager.verify(response_object['data'], response_object['sign'])
                    if(isVerified is True):
                        data_obj = json.loads(response_object['data'])
        
                        # decrypt symmetric key with receiver's/requester private key
                        decrypted_symmetric_key = encryptionManager.decrypt(data_obj['symmetric-key'], encryptionManager.private_key)                    
                        
                        print('Symmetric data decryption with symmetric key while data read request')
                        # decrypt data by using symmetric key
                        decrypted_data = encryptionManager.symetric_decrypt(data_obj['symmetric-data'], decrypted_symmetric_key)
                        
                        print(60 * "-")
                        print('data retrieved from client id: '+actor[0]['client_id'])
                        print(json.dumps(decrypted_data, indent=2))
                        print()
                    
                else:
                    print('Failed to read data from client id: ' + actor[0]['client_id'])

            except:
                print('Unable to read data')
                print(actor[0]['client_id'] + ' peer might be unavailable.')
            
            
            CSVLogger.timeObj['OverallTime'] = (time.perf_counter()-start_time)
            print("\nOverall time to read data (blockchain, data request, ring verification, decryption):", format((time.perf_counter()-start_time), '.8f'))
            
            print("\nData request time (time taken by owner to decrypt, create ring and return data):", format((time.perf_counter()-req_time), '.8f'))

            # save current run time
            CSVLogger.save_time()

        CSVLogger.sym_read_data_csv()
    else:
        print(actor_id + ' is unavailable or not valid in tree/hierarchy.')
    
def delete_data(block):
    for i in range(test_run):
        CSVLogger.timeObj = {}
        # simulate rbac time again 
        rbac.verify_permission(client_role, 'delete', 'blockchain') # - required for test run only
        CSVLogger.timeObj['RbacTime'] = rbac.permission_time

        # simulate read and decryption time again
        read_my_data() # - required for test run only
        
        start_time = time.perf_counter()

        # extract pointer from existing block
        pointer = block['data']
        # 'DELETED' will identify that data is deleted
        dht_manager.set_value(pointer, 'DELETED')
        if 'previous_pointers' in block:
            # delete update history data
            for prev_pointer in block['previous_pointers']:
                dht_manager.set_value(prev_pointer, 'DELETED')

        CSVLogger.timeObj['OverallTime'] = (time.perf_counter()-start_time)+rbac.permission_time+CSVLogger.timeObj['EncDecTime']+CSVLogger.timeObj['BlockchainReadTime']
        print("\nOverall time to delete data on dht:", format(CSVLogger.timeObj['OverallTime'],'.8f'))
        
        print('Data deleted on DHT.')
        CSVLogger.save_time()
    CSVLogger.delete_data_csv()
    
def decrypt_block_content(block):
    # extract pointer from block object
    pointer = block['data']

    # retrieve data from dht against provided pointer
    dht_data = dht_manager.get_value(pointer)

    # check if dht_data is deleted then retun None
    if(dht_data == 'DELETED'):
        print('DHT data is deleted.')
        return None
    # id dht data is available then decrypt it
    elif dht_data is not None:
        decrypted_data = None
        dht_data = json.loads(dht_data)
        
        # if data is encrypted with public key then decrypt data with owner's private key
        if('asymmetric-data' in dht_data):
            print('Asymmetric decryption time with owner key while data read request')
            decrypted_data = encryptionManager.decrypt(dht_data['asymmetric-data'], encryptionManager.private_key)                    
            print("Data is decrypted using owner's private key")
            
        # if data is encrypted with symmetric key
        elif('symmetric-data' in dht_data):
            print('Symmetric key decryption with owners public key while data read request')
            # decrypt symmetric key with owner's private key
            decrypted_symmetric_key = encryptionManager.decrypt(dht_data['symmetric-key'], encryptionManager.private_key)                    
            
            print('Symmetric data decryption with symmetric key while data read request')
            # decrypt data by using symmetric key
            decrypted_data = encryptionManager.symetric_decrypt(dht_data['symmetric-data'], decrypted_symmetric_key)
            
            print("Data is decrypted using symmetric key")

        if decrypted_data is not None:
            decrypted_data['meta-data'] = block['meta-data']
            decrypted_data['data'] = pointer

            return decrypted_data
        else:
            return None
# Data owner will read his own data and decrypt, and return data 
def read_my_data():
    CSVLogger.timeObj['EncDecTime'] = 0
    CSVLogger.timeObj['DhtRead'] = 0
    
    bc_start_time=time.perf_counter()        
    # variable to store all transactions
    transactions = []
    for block in blockChainManager.blockchain.chain:
        transactions.extend(block.transactions)
    
    CSVLogger.timeObj['BlockchainReadTime'] = (time.perf_counter()-bc_start_time)
    
    # current actor's transactions, and match current client id from metedatadata and then if match then transaction
    transactions = [t for t in transactions if t['meta-data']['client-id'] == client_id]
    # decrypt all transactions
    decrypted_data = []
    for transaction in transactions:
        # set initial time to 0 (actual time will be updated in decrypt_block_content function)
        CSVLogger.timeObj['AsymmetricDecryption'] = 0
        CSVLogger.timeObj['SymmetricDecryption'] = 0

        data = decrypt_block_content(transaction)
        CSVLogger.timeObj['EncDecTime'] += CSVLogger.timeObj['AsymmetricDecryption']
        CSVLogger.timeObj['EncDecTime'] += CSVLogger.timeObj['SymmetricDecryption']
        if data is not None:
            decrypted_data.append(data)

    update_history_time = time.perf_counter()
    # maintain transactions history by checking previous pointer
    decrypted_data = maintain_update_history(decrypted_data, [])
    # mintain pointer time
    CSVLogger.timeObj['MaintainUpdateHistoryTime'] = (time.perf_counter()-update_history_time)
    
    return decrypted_data

# manage previos pointer and new pointer in BC
def maintain_update_history(transactions, previous_pointers):
    transactions_history = []
    
    # pseudo code
    for transaction in transactions:
        # check if any previouse pointer exists in the transactions(match previous pointer with currrent data)
        history_found = [t for t in transactions if t['meta-data']['previous_pointer'] == transaction['data']]
        # history found so process it recursiverly
        if len(history_found)>0:
            previous_pointers.append(transaction['data'])

            # history found so save previous data in same transaction
            history_found[0]['previous_data']=transaction
            
            # call same update history function recursiverly to check the previous history of that found transaction, e.g 1, 2, 3
            maintain_update_history(history_found, previous_pointers)
        # history not found so save transaction in transaction_history variable
        else:
            if 'previous_data' not in transaction:
                transaction['previous_data'] = {}
                # store all previous pointers for this transaction
            transaction['previous_pointers']=previous_pointers
            transactions_history.append(transaction)
        
    return transactions_history

def display_menu():
    def print_menu():
        print(30 * "-", client_name, "-", client_role, "- ID: ", client_id, 30 * "-")
        print("1. Create data ")
        print("2. Read data ")
        print("3. Update data ")
        print("4. Delete data ")
        print("5. Display peers ")
        print("6. Mine transactions ")
        print("7. Display my tree/hierarchy ")
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
                data_input()
            else:
                print('You are not authorized to perform this action.')
            
        elif choice == '2':

            # read data
             # verify permission
            if(rbac.verify_permission(client_role, 'read', 'blockchain')):
                read_data()
            else:
                print('You are not authorized to perform this action.')
            
        elif choice == '3':
            # update data
            # verify permission
            if(rbac.verify_permission(client_role, 'update', 'blockchain')):
                # return all confirmed transactions after mining to the data owner/ read data for update it
                all_data = read_my_data()
                if len(all_data)==0:
                    print('No data available for update')
                else:
                    # display transactions and print transaction number with data
                    for data in all_data:
                        # remove previous data object from data (so that only recent data can be displayed to user)
                        del data['previous_data']
                        print('Transaction number:', all_data.index(data))
                        print(json.dumps(data, indent=2))
                        print(30 * '-')
                    
                    # ask transaction number to update it
                    transactionNumber = ''
                    while len(transactionNumber) == 0:
                        transactionNumber = input("Please enter transaction number to update data: ")
                        if (transactionNumber.isnumeric() == False or int(transactionNumber) > len(all_data)-1):
                            print('Invalid transaction number')
                            transactionNumber=''

                    # get block/transaction that user has requested to updated
                    block = all_data[int(transactionNumber)]

                    # if block found then take new input from user to update data
                    if(block is not None):
                        # check if current user id is not owner of this data
                        if block['meta-data']['client-id'] != client_id:
                            print('You can not modify this data.')
                        else:
                            data_input(block)
            else:
                print('You are not authorized to perform this action.')

        elif choice == '4':
            # delete data
             # verify permission
            if(rbac.verify_permission(client_role, 'delete', 'blockchain')):
                # return all confirmed transactions for delete
                all_data = read_my_data()
                if len(all_data)==0:
                    print('No data available for delete')
                else:
                    # display transactions and print transaction number with data
                    for data in all_data:
                        # remove previous data object from data (so that only recent data can be displayed to user)
                        del data['previous_data']
                        print('Transaction number:', all_data.index(data))
                        print(json.dumps(data, indent=2))
                        print(30 * '-')
                    
                    # ask transaction number to delete it
                    transactionNumber = ''
                    while len(transactionNumber) == 0:
                        transactionNumber = input("Please enter transaction number to delete it: ")
                        if (transactionNumber.isnumeric() == False or int(transactionNumber) > len(all_data)-1):
                            print('Invalid transaction number')
                            transactionNumber=''

                    # get block/transaction that user has requested to delete
                    block = all_data[int(transactionNumber)]

                    if(block is not None):
                        # check if current user is not owner of this data
                        if block['meta-data']['client-id'] != client_id:
                            print('You can not modify this data.')
                        else:
                            delete_data(block)
            else:
                print('You are not authorized to perform this action.')

        elif choice == '5':
            # display available peers
            for peer in peer_list:
                print(30 * "-")
                print("client address: ", peer['client_address'])
                print("client name: \t", peer['client_name'])
                print(30 * "-")
                
            loop=True
        
        elif choice == '6':
            # mine unconfirmed transactions and announce block to all peers (multišple transactions will be stored in one block)
            result = blockChainManager.mine_unconfirmed_transactions()
            print(result)

        elif choice == '7':
            for peer in my_actors_tree:
                print(30 * "-")
                print('client_name: '+peer['client_name'])
                print('client_id: '+peer['client_id'])
                print(30 * "-")
                
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
    parser.add_argument('-p', '--port', default=8020, type=int, help='port to listen on')
    parser.add_argument('-c', '--client', default='wood_cutting', help='Enter client name')
    parser.add_argument('-r', '--role', default='owner', help='Enter role name')
    parser.add_argument('-id', '--id', default='wood_cutting1-3', help='Enter role name')
    
    args = parser.parse_args()
    port = args.port
    client_name = args.client
    client_role = args.role
    client_id = args.id

    # authenticate client name and role using rabac manager
    if(not rbac.authenticate(client_name, client_role)):
        print('Not authenticated.')
        exit()
    
    # create object of encryption manager class
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