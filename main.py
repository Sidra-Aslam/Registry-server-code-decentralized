import logging
from flask import Flask, request, jsonify
from argparse import ArgumentParser
import json
import requests
import threading
from blockchain_manager import BlockchainManager
from kademlia.network import Server
import asyncio
from urllib.parse import urlparse


# dht node
dht_node = Server()

# variable to store perrs list
peer_list = set()
# blockchain manager object
blockChainManager = BlockchainManager()

# port at which client api is running
port = None

# url on which registry server is running
registry_server = None

# api url on which current program is running
my_endpoint = None

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

# start dht node
# this will be conntected with the first dht node 
def start_dht_node():
    # global variable to store current dht node
    global dht_node
    
    # variable to store existing dht nodes
    dht_other_nodes = []
    # iterate all available peers
    for peer in peer_list:
        # 'http://localhost:8092'
        if peer != my_endpoint:
            endpoint = urlparse(peer)
            # append dht host and port number of other node to dht_other_nodes variable
            dht_other_nodes.append((endpoint.hostname, endpoint.port+1))

    # to display kademlia log information in console
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    # create loop on which current dht node will be running
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    # start listening current node on network
    loop.run_until_complete(dht_node.listen(port+1))

    # if there is any existing dht node then connect current node to all other nodes
    if(len(dht_other_nodes)>0):
        loop.run_until_complete(dht_node.bootstrap(dht_other_nodes))
    else:
        print('DHT first node started')
    
    try:
        # run loop all the time
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        dht_node.stop()
        loop.close()
    
    
    # i.e usage
    # this value will be available on all the nodes connected
    
    

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8098, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    registry_server = "http://127.0.0.1:8080/"
    my_endpoint = "http://127.0.0.1:"+str(port)
    print("Registry Server Url: "+registry_server)

    # start new process for flask http api
    flaskProcess = threading.Thread(target=app.run, kwargs={'host':'0.0.0.0', 'port': port, 'debug': False})
    # flaskProcess.daemon = True
    flaskProcess.start()
    
    initialize_components()


    # start new process for flask http api
    dhtThread = threading.Thread(target=start_dht_node)
    # dhtThread.daemon = True
    dhtThread.start()
    
    # start dht node
    # asyncio.run(start_dht_node())
    
