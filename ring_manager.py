#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from ring import Ring
import json
import binascii
from time import perf_counter
class RingManager:
    def __init__(self, pub_key, pvt_key, peers):
        # variable to hold current user private key + public key and all other users public keys
        keys = []

        # import private key of signer/ create object of private key
        pv_key = RSA.importKey(pvt_key)
        keys.append(pv_key)
        
        # import public key of signer/ create object of public key
        pu_key = RSA.importKey(pub_key)
        keys.append(pu_key)
        
        # import public keys of all other peers
        for peer in peers:
            pu_key = RSA.importKey(peer['public_key'])
            keys.append(pu_key)

        # create ring object using signer's private key and all public keys of other peers
        self.ring = Ring(keys)

    # method to sign data
    def sign(self, data):
        start_time=perf_counter()
        data = json.dumps(data)
        # create signature using signer's private key which is at first index in the keys list e.g 0
        signature = self.ring.sign(data, 0)
        print("\nTime to Just create ring sign:", format((perf_counter()-start_time), '.8f'))
        print('Ring signature created')
        # convert signature to string format
        return ','.join(map(str, signature))

    # method to verify signature and data
    def verify(self, data, signature):
        start_time=perf_counter()
        data = json.dumps(data)
        # convert signature from string to list object
        sign = list(map(int, signature.split(',')))
        # verify signature
        isVerified = self.ring.verify(data, sign)
        print("\nTime to Just verify ring sign:", format((perf_counter()-start_time), '.8f'))
        if(isVerified):
            print('Ring is verified')
        else:
            print('Ring verification failed')
        return isVerified



