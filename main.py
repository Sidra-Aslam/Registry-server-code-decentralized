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

test_run = 1

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

# shared messages
messages = []

# create flask app object
app = Flask(__name__)

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
    
    peer_list = list(request.get_json())
    # remove my endpoint from peer list
    peer_list = [p for p in peer_list if p['client_address'] != my_endpoint]

    if(blockChainManager is not None):
        blockChainManager.peers = peer_list

    # create object of ring manager using signer's private key and all public keys of other peers
    ring_manager = RingManager(encryptionManager.public_key, encryptionManager.private_key, peer_list)
    

    print('Peer list updated')
    return ('', 200)

# api /chain to return blockchain copy or replicate block on peers
# this will be called from any other client

@app.route('/chain', methods=['GET', 'POST']) # route mapping with get/post request
@app.route('/chain/<block_no>', methods=['POST']) # route mapping with post and block number (for request data)
def chain(block_no=None):
    global blockChainManager
    global peer_list

    # return blockchain copy
    if request.method == 'GET' and block_no is None:
        chain_data = []
        # iterate all blocks from blockchain
        for block in blockChainManager.blockchain.chain:
            chain_data.append(block.__dict__)
        
        return jsonify(chain_data)
    
    # for requester
    # get method and there is block number, so return the data from location
    elif request.method == 'POST' and block_no is not None:
        # get requester role and name
        requester = request.get_json()
        block = blockChainManager.findblock(block_no)
        # decrypt data
        data, read_type = decrypt_block_content(block)
        

        # role is public user
        if requester['role'] == 'public_user':
            data = data['public']

        # role is business partner or role is owner of other company
        # client id condition is added to handle the case when same client requests the data who has created it
        elif requester['role'] == 'business_partner' or (requester['role'] == 'owner' and requester['client_id'] != client_id):
            # remove private data from data object
            del data['private']
        
        # current peer information
        peer = [{"client_address": my_endpoint, "client_id": client_id, 'public_key': encryptionManager.public_key}]
        
        # clinet_name is a current login user. and requester is a user who reads data
        # if data owner is not current user then look for owner endpoint from peer_list
        if client_id != requester['client_id']:
            # get one peer endpoint from peer_list to find out data requester's enspoint 
            peer = [p for p in peer_list if p['client_id'] == requester['client_id']]
        
        if len(peer) > 0:
            requester_public_key = peer[0]['public_key']
            print('Asymmetric data encryption with requesters public key while data read request')
            # encrypt data with requester's public key
            encrypted_data = encryptionManager.encrypt(data, requester_public_key)
            CSVLogger.timeObj['EncDecTime'] += CSVLogger.timeObj['AsymmetricEncryption']
            
            # create ring signature of encrypted dtaa
            sign = ring_manager.sign(encrypted_data)
            # return signature and encrypted data to requester
            return jsonify({'sign':sign,'data':encrypted_data, 'enc_type':read_type, 'timeObj':CSVLogger.timeObj})

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
        {"client_address": my_endpoint, "client_name": client_name, "public_key": encryptionManager.public_key}), headers=headers)         

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

# data input function for occupant actor
def occupant_data_input(block=None):

    # occupant actor data object to hold private data
    private_data = {'ConsumerId': '', 'ComfortPreference': {}, 'Temperature':''}
    # occupant actor data object to hold sensitive data
    sensitive_data = {'Schedule': {}}
    # occupant actor data object to hold public data
    public_data = {'ConsumptionMix': {}}

    # take private data from actor
    while len(private_data['ConsumerId']) == 0:
        private_data['ConsumerId'] = input("Consumer Id: ")
    
    print("Enter multiple inputs in format as -> key : value, ")
    while len(private_data['ComfortPreference']) == 0:
        input_text = input('Enter Comfort Preference as key value pairs (text, float):')
        private_data['ComfortPreference'] = format_key_value(input_text, 'text')

    while len(private_data['Temperature']) == 0:
        private_data['Temperature'] = input("Temperature: ")
    
    # take privacy sensitive data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(sensitive_data['Schedule']) == 0:
        input_text = input('Enter Schedule as key value pairs (text, bool -> 0/1):')
        # convert input values to json format with int conversion
        sensitive_data['Schedule'] = format_key_value(input_text, 'int')


    # take public data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(public_data['ConsumptionMix']) == 0:
        input_text = input('Enter Consumption Mix as key value pairs (text, float):')
        # convert input values to json format with float conversion
        public_data['ConsumptionMix'] = format_key_value(input_text, 'float')

    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        create_data(data)
    else:
        update_data(data, block)


# data input function for household actor
def household_data_input(block=None):

    # household actor data object to hold private data
    private_data = {'ConsumerId': '', 'PerformanceDataForAppliances': {}}
    # household actor data object to hold sensitive data
    sensitive_data = {'MeasureConsumption': {}}
    # household actor data object to hold public data
    public_data = {'HouseholdSize': ''}

    # take private data from actor
    while len(private_data['ConsumerId']) == 0:
        private_data['ConsumerId'] = input("Consumer Id: ")
    
    print("Enter multiple inputs in format as -> key : value, ")
    while len(private_data['PerformanceDataForAppliances']) == 0:
        input_text = input('Enter Performance Data For Appliances as key value pairs (text, float):')
        # convert input values to json format with float conversion
        private_data['PerformanceDataForAppliances'] = format_key_value(input_text, 'float')

    # take privacy sensitive data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(sensitive_data['MeasureConsumption']) == 0:
        input_text = input('Enter Measure Consumption as key value pairs (text, float):')
        # convert input values to json format with float conversion
        sensitive_data['MeasureConsumption'] = format_key_value(input_text, 'float')

    # take public data from actor
    while len(public_data['HouseholdSize']) == 0:
        public_data['HouseholdSize'] = input("Household Size: ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        create_data(data)
    else:
        update_data(data, block)

# data input function for building actor
def building_data_input(block=None):

    # building actor data object to hold private data
    private_data = {'ConsumerId': '', 'ThermalTransmittance': {}}
    # building actor data object to hold sensitive data
    sensitive_data = {'EnergyConsumption': {}}
    # building actor data object to hold public data
    public_data = {'BuildingLocation': ''}

    # take private data from actor
    while len(private_data['ConsumerId']) == 0:
        private_data['ConsumerId'] = input("Consumer Id: ")
    
    print("Enter multiple inputs in format as -> key : value, ")
    while len(private_data['ThermalTransmittance']) == 0:
        input_text = input('Enter Thermal transmittance of building envelope as key value pairs (text, float):')
        # convert input values to json format with float conversion
        private_data['ThermalTransmittance'] = format_key_value(input_text, 'float')

    # take privacy sensitive data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(sensitive_data['EnergyConsumption']) == 0:
        input_text = input('Enter Energy Consumption as key value pairs (text, float):')
        # convert input values to json format with float conversion
        sensitive_data['EnergyConsumption'] = format_key_value(input_text, 'float')

    # take public data from actor
    while len(public_data['BuildingLocation']) == 0:
        public_data['BuildingLocation'] = input("Building Location: ")
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        create_data(data)
    else:
        update_data(data, block)
    
# data input function for community actor
def community_data_input(block=None):

    # community actor data object to hold private data
    private_data = {'ConsumerId': '', 'PerformanceDataForPowerPlant': {}}
    # community actor data object to hold sensitive data
    sensitive_data = {'EnergyProduction': {}}
    # community actor data object to hold public data
    public_data = {'ShareOfRenewables': {}}

    # take private data from actor
    while len(private_data['ConsumerId']) == 0:
        private_data['ConsumerId'] = input("Consumer Id: ")
    
    print("Enter multiple inputs in format as -> key : value, ")
    while len(private_data['PerformanceDataForPowerPlant']) == 0:
        input_text = input('Enter Performance data for power plant as key value pairs (text, float):')
        # convert input values to json format with float conversion
        private_data['PerformanceDataForPowerPlant'] = format_key_value(input_text, 'float')

    # take privacy sensitive data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(sensitive_data['EnergyProduction']) == 0:
        input_text = input('Enter Energy Production as key value pairs (text, float):')
        # convert input values to json format with float conversion
        sensitive_data['EnergyProduction'] = format_key_value(input_text, 'float')

    # take public data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(public_data['ShareOfRenewables']) == 0:
        input_text = input('Enter Share of renewables in energy production as key value pairs (text, float):')
        # convert input values to json format with float conversion
        public_data['ShareOfRenewables'] = format_key_value(input_text, 'float')
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        create_data(data)
    else:
        update_data(data, block)

# data input function for dso actor
def dso_data_input(block=None):

    # dso actor data object to hold private data
    private_data = {'DistributionLosses': {}}
    # dso actor data object to hold sensitive data
    sensitive_data = {'EnergyProduction': {}}
    # dso actor data object to hold public data
    public_data = {'GridBalance': {}}

    # take private data from actor
    print("Enter multiple inputs in format as -> key : value, ")
    while len(private_data['DistributionLosses']) == 0:
        input_text = input('Enter Distribution Losses as key value pairs (text, float):')
        # convert input values to json format with float conversion
        private_data['DistributionLosses'] = format_key_value(input_text, 'float')

    # take privacy sensitive data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(sensitive_data['EnergyProduction']) == 0:
        input_text = input('Enter Energy Production as key value pairs (text, float):')
        # convert input values to json format with float conversion
        sensitive_data['EnergyProduction'] = format_key_value(input_text, 'float')

    # take public data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(public_data['GridBalance']) == 0:
        input_text = input('Enter GridBalance as key value pairs (text, float):')
        # convert input values to json format with float conversion
        public_data['GridBalance'] = format_key_value(input_text, 'float')
    
    # create data object
    data = {
        'private': private_data,
        'sensitive': sensitive_data,
        'public': public_data
    }

    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        create_data(data)
    else:
        update_data(data, block)

# data input function for government actor
def government_data_input(block=None):

    # government actor data object to hold sensitive data
    sensitive_data = {'CityScaleEnergy': {}}
    # government actor data object to hold public data
    public_data = {'GrantAmount': ''}

    # take privacy sensitive data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(sensitive_data['CityScaleEnergy']) == 0:
        input_text = input('Enter City Scale Energy as key value pairs (text, float):')
        # convert input values to json format with float conversion
        sensitive_data['CityScaleEnergy'] = format_key_value(input_text, 'float')

    # take public data from actor
    print("Enter multiple inputs in format as -> key : value,")
    while len(public_data['GrantAmount']) == 0:
        public_data['GrantAmount'] = input("Grant Amount: ")
    
    # create data object
    data = {
        'private': {},
        'sensitive': sensitive_data,
        'public': public_data
    }

    # if block is none then this fuction will used to take input and create new data
    # else block has some value then this fuction will used to take input and update existing data
    if(block is None):
        create_data(data)
    else:
        update_data(data, block)

# store data method
# pointer and meta data will be stored on blockchain
# actual data will be stored on dht
def create_data(data):
    encryption_method = ''
    # choose encryption method
    while len(encryption_method) == 0:
        encryption_method = input("choose encryption method symmetric/asymmetric?")
    
    # repeat the process n times
    for i in range(test_run):
        # clear time object for each run
        CSVLogger.timeObj = {}
        # verify permission again 
        rbac.verify_permission(client_role, 'write', 'blockchain') # - for test run
        
        start_time = time.perf_counter() + rbac.permission_time

        #take user id from private data
        user_id = ''
        if 'ConsumerId' in data['private']:
            user_id = data['private']['ConsumerId']
        
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

        # store pointer and meta data on blockchain (transaction will be added to unconfirmed list)
        blockChainManager.new_transaction(pointer, user_id, 'private-data', client_name, client_id)
        # mine unconfirmed transactions and announce block to all peers
        result = blockChainManager.mine_unconfirmed_transactions()
        
        CSVLogger.timeObj['BlockchainStorageTime'] = (time.perf_counter()-bc_start_time)
        CSVLogger.timeObj['OverallTime'] = (time.perf_counter()-start_time)
        
        print("\nTime to store pointer on blockchain without dht and decryption:", format((time.perf_counter()-bc_start_time), '.8f'))
        print("\nOverall time to create data (with encryption, dht, blockchain):", format((time.perf_counter()-start_time), '.8f'))
        
        print(result)
        # save time in list for current run
        CSVLogger.save_time()
    # create excel file based on encryption method
    if(encryption_method=='asymmetric'):
        CSVLogger.asym_create_data_csv()
    else:
        CSVLogger.sym_create_data_csv()

total_read_time = 0
overall_enc_time = 0
# read data 
# this function will return block
def read_data():
    # find block
    blockNo, block = blockChainManager.readblock()
    for i in range(test_run):
        CSVLogger.timeObj = {}
        
        # simulate rbac time again 
        rbac.verify_permission(client_role, 'read', 'blockchain') # - required for test run only
        
        # simulate find block time again
        blockChainManager.findblock(blockNo)  # - required for test run only

        # calculate start time to read data 
        start_time = time.perf_counter() + blockChainManager.find_block_time + rbac.permission_time
        
        read_type = None
        if(block is not None):
            # take data owner name from block meta data
            owner_name = block['meta-data']['client-name']
            # verify if the client is valid business partner
            if(rbac.check_business_partner(client_name, owner_name)==False):
                print('you are not business partner with '+owner_name+' so you can not read data.')
                return
            
            try:
            # read owner id from meta data
                owner_id = block['meta-data']['client-id']
                # find endpoint of owner
                peer = find_end_point(owner_id)

                if len(peer) > 0:
                    # data read request time
                    req_time = time.perf_counter()
                    headers = {'Content-Type': "application/json"}
                    # send data read request to owner to decrypt data
                    response = requests.post(peer[0]['client_address']+ "/chain/"+blockNo, 
                        data=json.dumps({'role': client_role, 'client_id':client_id}), headers=headers)
                    
                    if response.ok:
                        # response object return by owner
                        response_object = response.json()
                        print("\nData request time (time taken by owner to decrypt, create ring and return data):", format((time.perf_counter()-req_time), '.8f'))
                        read_type = response_object['enc_type']
                        timeObj = response_object['timeObj']
                        
                        CSVLogger.timeObj['EncDecTime'] =  timeObj['EncDecTime']
                        CSVLogger.timeObj['CreateRing'] =  timeObj['CreateRing']
                        CSVLogger.timeObj['DhtRead'] =  timeObj['DhtRead']
                        
                        # verify ring signature
                        isVerified = ring_manager.verify(response_object['data'], response_object['sign'])
                        if(isVerified is True):
                            print('Data decryption time with requesters public key when data is returned from owner')
                            # decrypte data with requester's/reader private key
                            plain_text = encryptionManager.decrypt(response_object['data'], encryptionManager.private_key)
                            CSVLogger.timeObj['OverallTime'] = (time.perf_counter()-start_time)
                            print("\nOverall time to read data (blockchain, data request, ring verification, decryption):", format((time.perf_counter()-start_time), '.8f'))
                            
                            # print data that is returned
                            print(plain_text)
                    else:
                        print('Failed to read data')
                else:
                    print(owner_id + ' peer is unavailable.')
            except:
                print('Unable to read data')
                print(owner_name + ' peer might be unavailable.')
        else:
            print('block not found')
        # save current run time
        CSVLogger.save_time()
    
    # save csv file for read data
    if(read_type=='asymmetric'):
        CSVLogger.asym_read_data_csv()
    else:
        CSVLogger.sym_read_data_csv()

def update_data(data, block):
    encryption_method = ''
    # choose encryption method
    while len(encryption_method) == 0:
        encryption_method = input("choose encryption method symmetric/asymmetric?")
    
    for i in range(test_run):
        CSVLogger.timeObj = {}
        # simulate rbac time again 
        rbac.verify_permission(client_role, 'update', 'blockchain') # - required for test run only
        
        # simulate find block time again
        blockChainManager.findblock(blockChainManager.find_block_no)  # - required for test run only
        
        start_time = time.perf_counter()  + rbac.permission_time

        # if user choose asymmetric encryption option
        if(encryption_method == 'asymmetric'):
            print('Data encrypt with owners public key while updating data')
            # encrypt data with public key
            encrypted_data = encryptionManager.encrypt(data, encryptionManager.public_key)
            encrypted_data = json.dumps({'asymmetric-data': encrypted_data})

        # if user choose symmetric encryption option
        elif(encryption_method=='symmetric'):
            print('Data encrypt with symmetric key while updating data')
            # encrypt data with symmetric key
            encrypted_data, symmetric_key = encryptionManager.symetric_encrypt(data)
            print('Encrypt symmetric key with owner public key while updating data')
            # encrypt symmetric key with owner's public key
            encrypted_key = encryptionManager.encrypt(symmetric_key, encryptionManager.public_key)
            # create data object with symmetric data and symmetric key
            encrypted_data = json.dumps({'symmetric-data': encrypted_data, 'symmetric-key': encrypted_key})
        else:
            print('Invalid encryption method')
            return None

        # extract pointer from existing block
        pointer = block['data']

        # store data on dht node
        dht_manager.set_value(pointer, encrypted_data)

        CSVLogger.timeObj['OverallTime'] = (time.perf_counter()-start_time)
        print("\nOverall time to update data (with encryption, dht):", format((time.perf_counter()-start_time), '.8f'))
        
        print('data updated')
        CSVLogger.save_time()
    
    if(encryption_method=='asymmetric'):
        CSVLogger.asym_update_data_csv()
    else:
        CSVLogger.sym_update_data_csv()

def delete_data(block):
    for i in range(test_run):
        CSVLogger.timeObj = {}
        # simulate rbac time again 
        rbac.verify_permission(client_role, 'delete', 'blockchain') # - required for test run only
        CSVLogger.timeObj['RbacTime'] = rbac.permission_time
        
        # simulate find block time again
        blockChainManager.findblock(blockChainManager.find_block_no)  # - required for test run only
        CSVLogger.timeObj['BlockchainReadTime'] = blockChainManager.find_block_time

        start_time = time.perf_counter() + rbac.permission_time
        # extract pointer from existing block
        pointer = block['data']
        # 'DELETED' will identify that data is deleted
        dht_manager.set_value(pointer, 'DELETED')
        CSVLogger.timeObj['OverallTime'] = (time.perf_counter()-start_time)+blockChainManager.find_block_time
        print("\nOverall time to delete data on dht:", format(((time.perf_counter()-start_time)+blockChainManager.find_block_time),'.8f'))
        
        print('Data deleted on DHT.')
        CSVLogger.save_time()
    CSVLogger.delete_data_csv()
def decrypt_block_content(block):
    CSVLogger.timeObj['EncDecTime']=0
    # extract pointer from block object
    pointer = block['data']

    # read metadata from block
    meta_data = block['meta-data']

    # get block privacy type e.g private, sensitive or public
    privacy_type = meta_data['privacy-type']
    
    # retrieve data from dht against provided pointer
    dht_data = dht_manager.get_value(pointer)

    # check if current role is valid to access block based on privacy type (private data, public data, privacy-sensitive data)
    if(rbac.verify_privacy(client_role, privacy_type) == False):
        print('You are not authorized to access this data.')
        return None

    # check if dht_data is deleted then retun None
    if(dht_data == 'DELETED'):
        print('DHT data is deleted.')
        return None

    elif dht_data is not None:
        decrypted_data = None
        dht_data = json.loads(dht_data)
        
        # if data is encrypted with public key then decrypt data with owner's private key
        if('asymmetric-data' in dht_data):
            read_type = 'asymmetric'
            print('Asymmetric decryption time with owner key while data read request')
            decrypted_data = encryptionManager.decrypt(dht_data['asymmetric-data'], encryptionManager.private_key)                    
            CSVLogger.timeObj['EncDecTime'] += CSVLogger.timeObj['AsymmetricDecryption']
            print("Data is decrypted using owner's private key")
            
        # if data is encrypted with symmetric key
        elif('symmetric-data' in dht_data):
            read_type = 'symmetric'
            print('Symmetric key decryption with owners public key while data read request')
            # decrypt symmetric key with owner's private key
            decrypted_symmetric_key = encryptionManager.decrypt(dht_data['symmetric-key'], encryptionManager.private_key)                    
            CSVLogger.timeObj['EncDecTime'] += CSVLogger.timeObj['AsymmetricDecryption']

            print('Symmetric data decryption with symmetric key while data read request')
            # decrypt data by using symmetric key
            decrypted_data = encryptionManager.symetric_decrypt(dht_data['symmetric-data'], decrypted_symmetric_key)
            CSVLogger.timeObj['EncDecTime'] += CSVLogger.timeObj['SymmetricDecryption']
            
            print("Data is decrypted using symmetric key")

        if decrypted_data is not None:
            return (decrypted_data, read_type)
        else:
            return None
# 0,1
# 0,1,2,0
# method to find endpoint based on parent
def find_end_point(owner_id):
    # find indexes in ids, we will use logic on these ids to identify 
    # if the client and data owner are in same group/hierarchy
    owner_indexes = re.findall(r'\d+', owner_id)
    client_indexes = re.findall(r'\d+', client_id)
    # check id indexes length, if they are equal then remove last index
    if(len(owner_indexes)==len(client_indexes)):
        owner_indexes.pop()
        client_indexes.pop()
    elif(len(owner_indexes)>len(client_indexes)):
        # consider client index length
        owner_indexes = owner_indexes[:len(client_indexes)]
    else:
        # consider owner index length
        client_indexes = client_indexes[:len(owner_indexes)]
    
    if(owner_id==client_id):
        # owner id is same as client id so return current endpoing details
        return [{"client_address": my_endpoint, "client_id": client_id}]
    elif(owner_indexes==client_indexes):
        # find peer details from peer_list based on owner id
        return [p for p in peer_list if p['client_id'] == owner_id]
    else:
        print('You can not read data from client '+owner_id)
        return []

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

def display_menu():
    def print_menu():
        print(30 * "-", client_name, "-", client_role, "- ID: ", client_id, 30 * "-")
        print("1. Create data ")
        print("2. Read data ")
        print("3. Update data ")
        print("4. Delete data ")
        print("5. Display peers ")
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
                if(client_name == 'occupant'):
                    occupant_data_input()
                elif(client_name == 'household'):
                    household_data_input()
                elif(client_name == 'building'):
                    building_data_input()
                elif(client_name == 'community'):
                    community_data_input()
                elif(client_name == 'dso'):
                    dso_data_input()
                elif(client_name == 'government'):
                    government_data_input() 

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
                # read block
                blockNo, block = blockChainManager.readblock()
                  
                # if block found then take new input from user to update data
                if(block is not None):
                    # check if current user is not owner of this data
                    if block['meta-data']['client-name'] != client_name:
                        print('You can not modify this data.')
                    elif(client_name == 'occupant'):
                        occupant_data_input(block)
                    elif(client_name == 'household'):
                        household_data_input(block)
                    elif(client_name == 'building'):
                        building_data_input(block)
                    elif(client_name == 'community'):
                        community_data_input(block)
                    elif(client_name == 'dso'):
                        dso_data_input(block)
                    elif(client_name == 'government'):
                        government_data_input(block)
            else:
                print('You are not authorized to perform this action.')

        elif choice == '4':
            # delete data
             # verify permission
            if(rbac.verify_permission(client_role, 'delete', 'blockchain')):
                # read block
                blockNo, block = blockChainManager.readblock()
                
                if(block is not None):
                    # check if current user is not owner of this data
                    if block['meta-data']['client-name'] != client_name:
                        print('You can not modify this data.')
                    else:
                        delete_data(block)
            else:
                print('You are not authorized to perform this action.')

        elif choice == '5':
            # display available peers
            for peer in peer_list:
                print("client address: ", peer['client_address'])
                print("client name: \t", peer['client_name'])
                print(60 * "-")
                
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
    parser.add_argument('-c', '--client', default='building', help='Enter client name')
    parser.add_argument('-r', '--role', default='owner', help='Enter role name')
    parser.add_argument('-id', '--id', default='government0-building0', help='Enter role name')
    
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