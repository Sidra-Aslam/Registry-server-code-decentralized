@ECHO OFF
start "Registry Server" python registry_server.py
timeout 2
start "main.py occupant, running on port 8060" python main.py --port 8060 --client occupant --role owner
timeout 2
start  "main.py household, running on port 8062" python main.py --port 8062 --client household --role owner
timeout 2
start "main.py building, running on port 8064" python main.py --port 8064 --client building --role public_user
timeout 2
start "main.py community, running on port 8066" python main.py --port 8066 --client community --role owner
timeout 2
start "main.py dso, running on port 8068" python main.py --port 8068 --client dso --role business_partner
timeout 2
start "main.py government, running on port 8070" python main.py --port 8070 --client government --role business_partner
ECHO All scripts are running...
PAUSE