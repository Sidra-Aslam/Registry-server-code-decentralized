start "Registry Server" python registry_server.py
timeout 2
start "main.py wood_cutting0-0, running on port 4998" python main.py --port 4998 --client wood_cutting --role owner --id wood_cutting0-0
timeout 2
start "main.py wood_cutting0-1, running on port 4996" python main.py --port 4996 --client wood_cutting --role business_partner --id wood_cutting0-1
timeout 2
start "main.py wood_cutting1-0, running on port 4992" python main.py --port 4992 --client wood_cutting --role owner --id wood_cutting1-0
timeout 2
start "main.py transport2-0, running on port 4986" python main.py --port 4986 --client transport --role owner --id transport2-0
timeout 2
start "main.py transport2-1, running on port 4984" python main.py --port 4984 --client transport --role business_partner --id transport2-1

