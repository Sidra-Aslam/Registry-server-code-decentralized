
# pip install cryptography
# https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/#:~:text=been%20installed%20correctly.-,What%20is%20Asymmetric%20Encryption%3F,you%20make%20them%20public%20information.

import cryptography, json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

class EncryptionManager:
   private_key = None
   public_key = None
   def __init__(self):
      # generate private key
      pvt_key = rsa.generate_private_key(public_exponent=65537,key_size=4096,backend=default_backend())
      
      # generate public key
      pub_key = pvt_key.public_key()

      # convert private key object format in string format
      self.private_key = pvt_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
      ).hex()

      # convert public key in string format
      self.public_key = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
      ).hex()
      print('Private Key: '+self.private_key)
      print('Public Key: '+self.public_key)
      
      
   def encrypt(self, data, pub_key):
      # convert data object to json string
      data = json.dumps(data).encode('ascii')
      
      # create public key object from string value
      public_key = serialization.load_pem_public_key(
         bytes.fromhex(pub_key),
         backend=default_backend()
      )
      # encrypt data by using public key
      encrypted = public_key.encrypt(data, 
      padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), 
      algorithm=hashes.SHA256(), label=None))
      
      # return encrypted data
      return encrypted.hex()

   def decrypt(self, encrypted, pvt_key):
      try:
         # convert key string back to original object
         private_key = serialization.load_pem_private_key(
            bytes.fromhex(pvt_key),
            password=None,
            backend=default_backend()
         )
         # decrypt message 
         original_message = private_key.decrypt(bytes.fromhex(encrypted), 
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
         
         # return original text
         decrypted_data = json.loads(original_message)

         return decrypted_data
         
      except Exception as e:
         print(str(e))
         return None

   def symetric_encrypt(self, data):
      # create symetric key
      key = Fernet.generate_key()
      
      # create Fernet class object (Fernet is used for symetric algorithm)
      f = Fernet(key)
      
      json_str = json.dumps(data).encode('ascii')
      
      #encrypt data with symetric key
      encrypted_text = f.encrypt(json_str).decode("utf-8")
      return (encrypted_text, key.decode()) 
   
   def symetric_decrypt(self, cypher_text, key):
      try:
         # create Fernet class object (Fernet is used for symetric algorithm)
         f = Fernet(key)
         
         # decrypt data
         plain_text = f.decrypt(cypher_text.encode('ascii'))
         
         return plain_text
      except Exception as e:
         print(str(e))
         return None
   