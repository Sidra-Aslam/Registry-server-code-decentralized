from flask import Flask, request, jsonify
from argparse import ArgumentParser
import json
import requests

# variable to store perrs list
peers = set()
# variable to store blockchain copy
chain = None
# port at which client api is running
port = None
# url on which registry server is running
registry_server= None

# create flask app object
app = Flask(__name__)

# api to register new client
# this will be called by registry server when new client will be connected
@app.route('/new_client', methods=['POST'])
def new_client():
    client_address = request.get_json()["client_address"]
    #add url of new client to the peers list
    peers.add(client_address)

# api to remove client from peers list
# this will be called by registry server when any client will be disconnected
@app.route('/disconnect_client', methods=['POST'])
def disconnect_client():
    client_address = request.get_json()["client_address"]
    # remove url from peer list
    peers.remove(client_address)

# method to connect new client with registry server
# and return list of all existing peers
def initialize_components():
    try:
        global peers
        headers = {'Content-Type': "application/json"}
        response = requests.post(registry_server+ "/connect_peer", data=json.dumps(
            {"client_address": "http://127.0.0.1:8090/"}), headers=headers)
        if(response.ok):
            peers = set(response.json()["peers"])
        else:
            print('Failed to connect with registry server.')
            exit()            

    except:
        print('Failed to connect with registry server.')
        exit()

if __name__ == '__main__':
    # create object of argument parser so we can access the option from cmd. i.e --port
    parser = ArgumentParser()
    # configure --port command in parser object and default values for reading --port
    parser.add_argument('-p', '--port', default=8081, type=int, help='port to listen on')
    
    # initialize argument parser
    args = parser.parse_args()
    # read --port value that user has entered in command line
    port = args.port
    registry_server = "http://localhost:8080/"
    
    initialize_components()
    print(peers)
