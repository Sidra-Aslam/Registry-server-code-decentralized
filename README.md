# Privacy-aware Distributed Ledger for Product Traceability in Supply Chain Environments


## Installation

Run following command to install required all libraries mentioned in 'requirements.txt':
```cmd
pip install -r requirements.txt
```

## Steps to run code


1. Run Registry Server (registry_server.py)
    ```
    python registry_server.py
    ```

2. Run main file (main.py)
    ```
    PEER1: python main.py --port 8060 --client wood_cutter --role owner
    PEER2: python main.py --port 8062 --client transporter --role business_partner
    ```

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
    * Check owner name in meta data
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
    * Check owner name in meta data
    * if owner name is same as current user then program will ask to enter new data
    * Enter encryption type
    * Encrypt data based on selected option
    * Update data on dht against the same pointer
    
4. Delete data
    > This option is used to delete data on dht. Program will ask user to enter block number to delete data then block is searched in user's local blockchain copy, if block is found program will perform following actions:
        * Check owner name in meta data
        * if owner name is same as current user then program will insert special veriable 'DELETED' on dht against the same pointer

5. Display peers
    > This option is used to display list of available peers.