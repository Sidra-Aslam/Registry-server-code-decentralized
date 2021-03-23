#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#https://github.com/bmuller/kademlia
from urllib.parse import urlparse
from kademlia.network import Server
import asyncio
import logging
import nest_asyncio
import threading
from time import perf_counter
from csv_log import CSVLogger

class DhtManager:
    def __init__(self, port, peer_list):
        self.port = port
        # By design asyncio does not allow its event loop to be nested
        # we used this to handle: RuntimeError: "This event loop is already running"
        nest_asyncio.apply()
        
        # variable to store other node addresses
        dht_other_nodes = []
        # iterate all available peers
#         old peer version: ["http:/localhost:8090", "http:/localhost:8090", "http:/localhost:8090"]
#         current peer version to represent client_address: [ {"client_name":"transport", "client_address":"http://127.0.0.1:8070"},
#           {"client_name":"customer", "client_address":"http://127.0.0.1:8072"}
#           ]
        for peer in peer_list:
            endpoint = urlparse(peer['client_address'])
            # append dht host and port number of other node to dht_other_nodes variable
            dht_other_nodes.append((endpoint.hostname, endpoint.port+1))

        # # to display log information
        # log = logging.getLogger('kademlia')
        # log.setLevel(logging.DEBUG)
        # log.addHandler(logging.StreamHandler())
        
        self.loop = asyncio.get_event_loop()
        # asyncio.set_event_loop(self.loop)
        # self.loop.set_debug(True)

        # create dht node object
        self.dht_node = Server()
        # start node on port + 1
        self.loop.run_until_complete(self.dht_node.listen(port))
        
        # if there is any existing dht node then connect current node to all other nodes
        if(len(dht_other_nodes) > 0):
            # connect with other dht nodes
            self.loop.run_until_complete(self.dht_node.bootstrap(dht_other_nodes))

    # method for main thread to continue running the node
    def start_node(self):
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.dht_node.stop()
            self.loop.close()
    
    def get_value(self, key):
        start_time = perf_counter()
        value = asyncio.run_coroutine_threadsafe(self.dht_node.get(key), self.loop).result()
        CSVLogger.timeObj['DhtRead'] = (perf_counter()-start_time)
        print("\nJust dht time to read data from dht:", format((perf_counter()-start_time), '.8f'))        
        return value

    def set_value(self, key, value):
        start_time = perf_counter()
        asyncio.run_coroutine_threadsafe(self.dht_node.set(key, value), self.loop).result()
        CSVLogger.timeObj['DhtStorage'] = (perf_counter()-start_time)
        print("\nJust dht time to store data on dht:", format((perf_counter()-start_time), '.8f'))
    