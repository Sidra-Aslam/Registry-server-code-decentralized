from flask import Flask, request, jsonify
import json
import requests

# create flask app object
app = Flask(__name__)

# the address to other participating members of the network
peers = set()

# return list of available peers that connected with registry server
@app.route('/peer_list', methods=['GET'])
def peer_list():
    # return all peers in json format
    return jsonify(list(peers))

# register new peer on registry server and broadcast it to existing peers
# and then return the list of all peers back to the new client as response
@app.route('/connect_peer', methods=['POST'])
def connect_peer():
    # get address (api url) of new client from request
    client_address = request.get_json()["client_address"]
    headers = {'Content-Type': "application/json"}

    # check if client address is not already in the peers list
    if client_address not in peers:
        # iterate all existing peers to acknowledge new client
        for peer in peers:
            try:
                # send request to other peers to acknowledge new client
                requests.post(peer + "/new_client", data=json.dumps(
                    {"client_address": client_address}), headers=headers)
            except:
                # if there is any error in communication then remove that peer from the peers list
                peers.remove(peer)

        # register new peer/client on registry server
        peers.add(client_address)

    # send list of existing peers to the new client
    return json.dumps({"peers": list(peers)})

# this api will be used to remove peer on registry server
# and registry server will anounce to all peers to remove this client
@app.route('/disconnect_peer', methods=['POST'])
def disconnect_peer():
    # get address (api url) of new client from request
    client_address = request.get_json()["client_address"]

    headers = {'Content-Type': "application/json"}
    # iterate all existing peers to remove peer from the list
    for peer in peers:
        try:
            # send request to other peers to remove this client
            requests.post(peer + "/disconnect_client", data=json.dumps(
                {"client_address": client_address}), headers=headers)
        except:
            peers.remove(peer)

    peers.remove(client_address)

if __name__ == '__main__':
    # run the flask app on the provided port
    app.run(debug=False, port=8080)