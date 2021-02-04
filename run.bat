@ECHO OFF
start "Registry Server" python registry_server.py
timeout 2
start "main.py wood_cutter, running on port 8060" python main.py --port 8060 --client wood_cutter --role owner
timeout 2
start  "main.py transporter, running on port 8062" python main.py --port 8062 --client transporter --role business_partner
timeout 2
start "main.py warehouse_storage, running on port 8064" python main.py --port 8064 --client warehouse_storage --role public_user
timeout 2
start "main.py furniture_assembly, running on port 8066" python main.py --port 8066 --client furniture_assembly --role owner
timeout 2
start "main.py furniture_shop, running on port 8068" python main.py --port 8068 --client furniture_shop --role business_partner
timeout 2
start "main.py customer, running on port 8070" python main.py --port 8070 --client customer --role public_user
ECHO All scripts are running...
PAUSE