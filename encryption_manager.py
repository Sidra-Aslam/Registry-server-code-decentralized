#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# pip install cryptography
# https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/#:~:text=been%20installed%20correctly.-,What%20is%20Asymmetric%20Encryption%3F,you%20make%20them%20public%20information.

import cryptography, json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
from time import perf_counter
from csv_log import CSVLogger
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
      ).decode()

      # convert public key in string format
      self.public_key = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
      ).decode()
      # print('Private Key: '+self.private_key)
      # print('Public Key: '+self.public_key)

   def encrypt(self, data, pub_key):
      start_time = perf_counter()
      # convert data object to json string
      data = json.dumps(data).encode('ascii')
      
      # create public key object from string value
      public_key = serialization.load_pem_public_key(
         pub_key.encode(),
         backend=default_backend()
      )
      # encrypt data by using public key
      encrypted = public_key.encrypt(data, 
      padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), 
      algorithm=hashes.SHA256(), label=None))
      CSVLogger.timeObj['AsymmetricEncryption'] = (perf_counter()-start_time)
      print("\nAsymmetric encryption time:", format((perf_counter()-start_time), '.8f'))

      # return encrypted data
      return encrypted.hex()

   def decrypt(self, encrypted, pvt_key):
      try:
         start_time = perf_counter()
         # convert key string back to original object
         private_key = serialization.load_pem_private_key(
            pvt_key.encode(),
            password=None,
            backend=default_backend()
         )
         # decrypt message 
         original_message = private_key.decrypt(bytes.fromhex(encrypted), 
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
         
         # return original text
         decrypted_data = json.loads(original_message)
         CSVLogger.timeObj['AsymmetricDecryption'] = (perf_counter()-start_time)
         print("\nAsymmetric decryption time:", format((perf_counter()-start_time), '.8f'))
      
         return decrypted_data
         
      except Exception as e:
         print(str(e))
         return None

   def symetric_encrypt(self, data):
      start_time = perf_counter()

      # create symetric key
      key = Fernet.generate_key()
      
      # create Fernet class object (Fernet is used for symetric algorithm)
      f = Fernet(key)
      
      json_str = json.dumps(data).encode('ascii')
      
      #encrypt data with symetric key
      encrypted_text = f.encrypt(json_str).decode("utf-8")
      CSVLogger.timeObj['SymmetricEncryption'] = (perf_counter()-start_time)
      print("\nSymmetric encryption time:", format((perf_counter()-start_time), '.8f'))
      
      return (encrypted_text, key.decode()) 
   
   def symetric_decrypt(self, cypher_text, key):
      try:
         start_time = perf_counter()
         # create Fernet class object (Fernet is used for symetric algorithm)
         f = Fernet(key)
         
         # decrypt data
         plain_text = f.decrypt(cypher_text.encode('ascii'))
         CSVLogger.timeObj['SymmetricDecryption'] = (perf_counter()-start_time)
         print("\nSymmetric decryption time:", format((perf_counter()-start_time),'.8f'))
      
         # return plain text in json format
         return json.loads(plain_text.decode("utf-8"))
      except Exception as e:
         print(str(e))
         return None
   
   def create_sign(self, data, pvt_key):
      # convert data object to json string
      data = json.dumps(data).encode()

      # convert key string back to original object
      private_key = serialization.load_pem_private_key(
         pvt_key.encode(),
         password=None,
         backend=default_backend()
      )
      # create signature for data using private key
      signature = private_key.sign(
         data,
         padding.PSS(
               mgf=padding.MGF1(hashes.SHA256()),
               salt_length=padding.PSS.MAX_LENGTH
         ),
         hashes.SHA256()
      )
      # return signature in string format
      return signature.hex()
   
   def verify_sign(self, data, signature, pub_key):
      try:
         # convert data object to json string
         data = json.dumps(data).encode()

         # create public key object from string value
         public_key = serialization.load_pem_public_key(
            pub_key.encode(),
            backend=default_backend()
         )
         # verify data and signature using public key
         public_key.verify(
            bytes.fromhex(signature),
            data,
            padding.PSS(
                  mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
         )
         print('Signature verified')
         return True
      except:
         print('Invalid signature')
         return False
