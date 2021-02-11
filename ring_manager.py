# https://github.com/fernandolobato/ecc_linkable_ring_signatures

from linkable_ring_signature import ring_signature, verify_ring_signature, concat, export_private_keys
from ecdsa import SigningKey
from ecdsa.util import randrange
from ecdsa.curves import SECP256k1
import ast
import json

class RingManager:
    # method to return private key of actor
    def get_actor_key(self, actor) -> tuple:
        # index of actor private key
        index = self.actors.index(actor)
        private_key = self._private_keys[index]
        return (private_key, index)

    # method to sign data
    def sign(self, private_key, public_key_index, data) -> tuple:
        # create signature using private key of current participant and all public keys
        signature = ring_signature(private_key, public_key_index, data, self._public_keys)
                
        return signature

    # method to verify signature and data
    def verify(self, signature, data) -> bool:
        # verify message with all public keys
        result = verify_ring_signature(data, self._public_keys, *signature)
        return result

    def __init__(self, actors):
        # list of actors
        self.actors = actors
        size = len(self.actors)

        # generate private keys for all actors
        self._private_keys = [randrange(SECP256k1.order) for i in range(size)]
        
        # generate public keys for all actors
        self._public_keys = list(map(lambda i: SECP256k1.generator * i, self._private_keys))
        pass

#------------------------
# for testing only

# list of companies
actors=["wood_cutter", "transporter", "warehouse_storage", "furniture_assembly",  "furniture_shop", "customer"]
#--------------------------------
wood_cutter_ring = RingManager(actors)

data="hello world"
# wood cutter creates signature
sign = wood_cutter_ring.sign(wood_cutter_ring._private_keys[0], 0, data)
print(sign)
# wood cutter verifies signature
verify = wood_cutter_ring.verify(sign, data)
print(verify)

#--------------------------------------------------
# transporter ring
transporter_ring = RingManager(actors)
# tansporter verifies signature which is created by wood cutter
verify = transporter_ring.verify(sign, data)

print(verify)