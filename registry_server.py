#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
from flask import Flask, request, jsonify
import json
import requests
import threading
import logging
import asyncio

# create flask app object
app = Flask(__name__)
# the address to other participating members of the network
peer_list = []

# the peers resource
@app.route('/peers', methods=['GET', 'POST'])
def peers():
    global peer_list
    if request.method == 'GET':
        # return all peers in json format
        return jsonify(list(peer_list))
    
    elif request.method == 'POST':
        remove_peers = []
        # add address (api url) and client_name of new client from request
        current_peer = request.get_json()
        
        headers = {'Content-Type': "application/json"}

        # client already in peer list
        peers = [p for p in peer_list if p['client_id'] == current_peer['client_id']]

       #if client is already in the list then disconnect it. 
        if (len(peers)):
            # remove peer from peer_list
            peer_list.remove(peers[0])
            # iterate all existing peers to acknowledge new client
            for peer in peer_list:
                try:
                    # send request to other peers to acknowledge new client
                    requests.post(peer['client_address'] + "/peers", data=json.dumps(list(peer_list)), headers=headers)
                except:
                    # if there is any error in communication then remove that peer from the peers list
                    remove_peers.append(peer)
            
            # remove not responding peers from main list
            for peer in remove_peers:
                peer_list.remove(peer)
             

        # check if client address is not already in the peers list
        else:
            # register new peer/client on registry server
            peer_list.append(current_peer)

            # iterate all existing peers to acknowledge new client
            for peer in peer_list:
                try:
                    # send request to other peers to acknowledge new client
                    requests.post(peer['client_address'] + "/peers", data=json.dumps(list(peer_list)), headers=headers)
                except:
                    # if there is any error in communication then remove that peer from the peers list
                    remove_peers.append(peer)
            
            # remove not responding peers from main list
            for peer in remove_peers:
                peer_list.remove(peer)
            
 
    print('Current peer list')
    #print(peer_list)
    
    return ('', 200)   

if __name__ == '__main__':
    app.run(debug=False, port=8080)
    
