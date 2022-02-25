# Privacy-aware Distributed Ledger for Data Management


## Installation

Run following command to install required all libraries mentioned in 'requirements.txt':
```cmd
pip install -r requirements.txt
```

Note: we recommend to use Anaconda framework because it provides most of of libraries pre-installed
## Steps to run code


1. Run Registry Server (registry_server.py)
    ```
    python registry_server.py
    ```

2. Run main file (main.py)
    ```
    PEER1: python main.py --port 8060 --client occupant --role owner
    PEER2: python main.py --port 8062 --client dso --role business_partner
    ```
## Prototype introduction
when any actor will be connected to the registry server then he will try to connect to any other available peer to copy blockchain.
Data create: To create/store the data on DHT, the current login actor (data owner) has 2 options to encrypt data (symmetric/asymmetric).
if owner chooses the asymmetric option then data will be encrypted with the owner's public key and stored on DHT.
if owner chooses the symmetric option then data will be encrypted with a symmetric key and the symmetric key again will be encrypted with the owner's public key, and then both (encrypted symmetric key + encrypted data) will be stored on DHT. Pointer + metatada and actor's name(data owner) will be stored on Blockchain.

Data read: when any other actor reads data, then our prototype will read block from his local blockchain copy and check for the data owner from metadata.
Then, a request is sent to the data owner through '/chain/xyz' --> block no endpoint. Owner will read the data from DHT, decrypt it and sign it by using ring signature and return it to the requester. The owner will check the requester's role and then returns data based on the requester's role. 

The authorized requester can read data and verify the ring signature 
## Menu options

1. Create data
    > This option is used to create new data. Following actions will be performed:
    * Check if current user role is owner
    * Take data input from user
    * Enter encryption type
    * Encrypt data based on encryption type
    * Store data on dht
    * Store pointer on blockchain with meta data
    * Replicate block to all available peers

2. Read data
    > This option is used to read data. Program will ask user to enter block number then block is searched in user's local blockchain copy, if block is found program will perform following actions:
  
    * Send data read request to owner
    * Owner reads blockchain for the requested data
    * Owner reads data from dht
    * Owner decrypts data
    * Owner encrypts data with requester's public key
    * Owner creates ring signature
    * Owner returns ring signature and encrypted data to requester
    * Requster verifies ring signature
    * Requester decrypts data with his private key
 
3. Update data
    > This option is used to modify data on dht. Program will ask user to enter block number to modify data then block is searched in user's local blockchain copy, if block is found program will perform following actions:
   
    * if owner name is same as current user then program will ask to enter new data
    * Enter encryption type
    * Encrypt data based on selected option
    * Update data on dht against the same pointer
    
4. Delete data
    > This option is used to delete data on dht. Program will ask user to enter block number to delete data then block is searched in user's local blockchain copy, if block is found program will perform following actions:
        
        * if owner name is same as current user then program will insert special veriable 'DELETED' on dht against the same pointer

5. Display peers
    > This option is used to display list of available peers.
