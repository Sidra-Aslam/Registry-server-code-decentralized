# Privacy-aware Distributed Ledger for Product Traceability in Supply Chain Environments


## Installation

Run following command to install required libraries:
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
    PEER1: python main.py --port 8092 --client wood_cutting 
    PEER2: python main.py --port 8090 --client transport
    ```
