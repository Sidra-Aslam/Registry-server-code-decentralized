start "main.py government1, running on port 4998" python main.py --port 4998 --client government --role owner --id government1
start "main.py government1-dso1, running on port 4996" python main.py --port 4996 --client dso --role owner --id government1-dso1
start "main.py dso1-community1, running on port 4994" python main.py --port 4994 --client community --role owner --id dso1-community1
start "main.py community1-building1, running on port 4992" python main.py --port 4992 --client building --role owner --id community1-building1
start "main.py building1-household1, running on port 4990" python main.py --port 4990 --client household --role owner --id building1-household1
start "main.py household1-occupant1, running on port 4988" python main.py --port 4988 --client occupant --role owner --id household1-occupant1
start "main.py household1-occupant2, running on port 4986" python main.py --port 4986 --client occupant --role owner --id household1-occupant2
