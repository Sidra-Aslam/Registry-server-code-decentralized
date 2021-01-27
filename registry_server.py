
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
        remove_peers = []
        # get address (api url) of new client from request
        client_address = request.get_json()["client_address"]
        headers = {'Content-Type': "application/json"}
        # check if client address is not already in the peers list
        if client_address not in peer_list:
            # register new peer/client on registry server
            peer_list.add(client_address)


            # iterate all existing peers to acknowledge new client
            for peer in peer_list:
                try:
                    # send request to other peers to acknowledge new client
                    requests.post(peer + "/peers", data=json.dumps(list(peer_list)), headers=headers)
                except:
                    # if there is any error in communication then remove that peer from the peers list
                    remove_peers.remove(peer)
            
            # remove not responding peers from main list
            for peer in remove_peers:
                peer_list.remove(peer)
            
        #if client is in the list it is a disconnect
        elif client_address in peer_list:
            # register new peer/client on registry server
            peer_list.remove(client_address)
            # iterate all existing peers to acknowledge new client
            for peer in peer_list:
                try:
                    # send request to other peers to acknowledge new client
                    requests.post(peer + "/peers", data=json.dumps(list(peer_list)), headers=headers)
                except:
                    # if there is any error in communication then remove that peer from the peers list
                    remove_peers.remove(peer)
            
            # remove not responding peers from main list
            for peer in remove_peers:
                peer_list.remove(peer)
            
    print('Current peer list')
    print(peer_list)
    
    return ('', 200)   

if __name__ == '__main__':
    app.run(debug=False, port=8080)
    
