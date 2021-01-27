from urllib.parse import urlparse
from kademlia.network import Server
import asyncio

class DhtManager:
    
    def __init__(self, node_address):
        self.current_node_address = node_address
    
    async def get_value(self, key):
        # create kademlia node object
        # this node will communitcate with the current dht node that is running on main.py
        node = Server()
        await node.listen(1111)
        await node.bootstrap([self.current_node_address])
        value = await node.get(key)
        node.stop()
        return value

    async def set_value(self, key, value):
        # create kademlia node object
        # this node will communitcate with the current dht node that is running on main.py
        node = Server()
        await node.listen(1111)
        await node.bootstrap([self.current_node_address])
        await node.set(key, value)
        node.stop()