
from flask import Flask, request, jsonify
import json
import requests
import threading
import logging
import asyncio
from kademlia.network import Server

# create flask app object
app = Flask(__name__)
# the address to other participating members of the network
peer_list = set()

# the peers resource
@app.route('/peers', methods=['GET', 'POST'])
def peers():
    global peer_list
    if request.method == 'GET':
        # return all peers in json format
        return jsonify(list(peer_list))
    
    elif request.method == 'POST':
        # get address (api url) of new client from request
        client_address = request.get_json()["client_address"]
        headers = {'Content-Type': "application/json"}
        # check if client address is not already in the peers list
        if client_address not in peer_list or True:
            # register new peer/client on registry server
            peer_list.add(client_address)
            # iterate all existing peers to acknowledge new client
            for peer in peer_list:
                try:
                    # send request to other peers to acknowledge new client
                    requests.post(peer + "/peers", data=json.dumps(list(peer_list)), headers=headers)
                except:
                    # if there is any error in communication then remove that peer from the peers list
                    peer_list.remove(peer)
                    
        #if client is in the list it is a disconnect
        elif client_address in peer_list:
            # register new peer/client on registry server
            peer_list.remove(client_address)
            # iterate all existing peers to acknowledge new client
            for i in range(len(peer_list)):
                peer = list(peer_list)[i]
                try:
                    # send request to other peers to acknowledge new client
                    requests.post(peer + "/peers", data=json.dumps(list(peer_list)), headers=headers)
                except:
                    # if there is any error in communication then remove that peer from the peers list
                    peer_list.remove(peer)

    print('Current peer list')
    print(peer_list)
    
    return ('', 200)   

# To start a new network, create the first node. 
# Future nodes will connect to this first node (and any other nodes you know about) 
# to create the network.
def run_dht_first_node():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)


    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    server = Server()
    loop.run_until_complete(server.listen(8081, interface='127.0.0.1'))
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()
        
if __name__ == '__main__':
    # start new process for flask http api
    flaskProcess = threading.Thread(target=app.run, kwargs={'host':'127.0.0.1', 'port': 8080, 'debug': False})
    # flaskProcess.daemon = True
    flaskProcess.start()
    
    # run first node on registry server
    run_dht_first_node()
    # run the flask app on the provided port

    # app.run(debug=False, port=8080)
    
