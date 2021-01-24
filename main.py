from flask import Flask, request, jsonify
from argparse import ArgumentParser
import json
import requests
import threading
from blockchain_manager import BlockchainManager

# variable to store perrs list
peer_list = set()
# blockchain manager object
blockChainManager = BlockchainManager()

# port at which client api is running
port = None

# url on which registry server is running
registry_server = None

# api url on which current program is running
my_api_url = None

# create flask app object
app = Flask(__name__)

# api to update whole peer list, this will be called by registry server
@app.route('/peers', methods=['POST'])
def peers():
    global peer_list
    peer_list = set(request.get_json())
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

# function to connect with registry server
def register():
    try:
        headers = {'Content-Type': "application/json"}
        req = requests.post(registry_server+ "/peers", data=json.dumps(
            {"client_address": my_api_url}), headers=headers)
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
        {"client_address": my_api_url}), headers=headers)         

# initialize blockchain copy
def initialize_blockchain():
    global blockChainManager
    global peer_list
    
    chain_initializer = None
    headers = {'Content-Type': "application/json"}
    for peer in peer_list:
        if peer != my_api_url:
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
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8091, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    registry_server = "http://localhost:8080/"
    my_api_url = "http://localhost:"+str(port)
    print("Registry Server Url: "+registry_server)

    # start new process for flask http api
    flaskProcess = threading.Thread(target=app.run, kwargs={'host':'0.0.0.0', 'port': port, 'debug': False})
    # flaskProcess.daemon = True
    flaskProcess.start()
    
    initialize_components()