start "Registry Server" python registry_server.py
timeout 2
start "main.py Alice - Woodcutter, running on port 4998" python main.py --port 4998 --client Alice --role Woodcutter
timeout 2
start "main.py Bob - Transporter, running on port 4996" python main.py --port 4996 --client Bob --role Transporter
timeout 2
start "main.py David - FurnitureShopOwner, running on port 4994" python main.py --port 4994 --client David --role FurnitureShopOwner
timeout 2
start "main.py Eric - FurnitureAssemblyManager, running on port 4992" python main.py --port 4992 --client Eric --role FurnitureAssemblyManager
timeout 2
start "main.py John - WarehouseManager, running on port 4990" python main.py --port 4990 --client John --role WarehouseManager
timeout 2
start "main.py Tim - Customer, running on port 4988" python main.py --port 4988 --client Tim --role Customer
timeout 2
