start "Registry Server" python registry_server.py
timeout 2
start "main.py government0, running on port 4998" python main.py --port 4998 --client government --role owner --id government0
timeout 2
start "main.py government0-dso, running on port 4996" python main.py --port 4996 --client dso --role owner --id government0-dso
timeout 2
start "main.py government0-community, running on port 4994" python main.py --port 4994 --client community --role owner --id government0-community
timeout 2
start "main.py government0-building0, running on port 4992" python main.py --port 4992 --client building --role owner --id government0-building0
timeout 2
start "main.py government0-building0-household0, running on port 4990" python main.py --port 4990 --client household --role owner --id government0-building0-household0
timeout 2
start "main.py government0-building0-household0-occupant0, running on port 4988" python main.py --port 4988 --client occupant --role owner --id government0-building0-household0-occupant0
