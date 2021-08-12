@ECHO OFF
start "Registry Server" python registry_server.py
timeout 2
start "main.py occupant, running on port 8060" python main.py --port 8060 --client communit --role owner --id community1
timeout 2
start "main.py occupant, running on port 8092" python main.py --port 8092 --client building --role owner --id building1 --community
timeout 2
start "main.py occupant, running on port 8094" python main.py --port 8094 --client household --role owner --id household1 --building1
timeout 2
start "main.py occupant, running on port 8096" python main.py --port 8096 --client household --role owner --id household2 --building1
timeout 2
start "main.py occupant, running on port 8098" python main.py --port 8098 --client household --role owner --id household3 --building1
timeout 2
start "main.py occupant, running on port 8058" python main.py --port 8058 --client occupant --role owner --id occupant1 --household1-building1
timeout 2
start "main.py occupant, running on port 8056" python main.py --port 8056 --client occupant --role owner
timeout 2
start "main.py occupant, running on port 8054" python main.py --port 8054 --client occupant --role owner
timeout 2
start "main.py occupant, running on port 8052" python main.py --port 8052 --client occupant --role owner
timeout 2
start "main.py occupant, running on port 8050" python main.py --port 8050 --client occupant --role owner
timeout 2
start  "main.py household, running on port 8062" python main.py --port 8062 --client household --role owner
timeout 2
start  "main.py household, running on port 8048" python main.py --port 8048 --client household --role owner
timeout 2
start  "main.py household, running on port 8046" python main.py --port 8046 --client household --role owner
timeout 2
start  "main.py household, running on port 8044" python main.py --port 8044 --client household --role owner
timeout 2
start  "main.py household, running on port 8042" python main.py --port 8042 --client household --role owner
timeout 2
start  "main.py household, running on port 8040" python main.py --port 8040 --client household --role owner
timeout 2
start  "main.py household, running on port 8038" python main.py --port 8038 --client household --role owner
timeout 2
start  "main.py household, running on port 8036" python main.py --port 8036 --client household --role owner
timeout 2
start  "main.py household, running on port 8034" python main.py --port 8034 --client household --role owner
timeout 2
start  "main.py household, running on port 8032" python main.py --port 8032 --client household --role owner
timeout 2
start "main.py building, running on port 8064" python main.py --port 8064 --client building --role public_user
timeout 2
start "main.py building, running on port 8030" python main.py --port 8030 --client building --role public_user
timeout 2
start "main.py building, running on port 8028" python main.py --port 8028 --client building --role public_user
timeout 2
start "main.py building, running on port 8026" python main.py --port 8026 --client building --role public_user
timeout 2
start "main.py building, running on port 8024" python main.py --port 8024 --client building --role public_user
timeout 2
start "main.py building, running on port 8022" python main.py --port 8022 --client building --role public_user
timeout 2
start "main.py building, running on port 8020" python main.py --port 8020 --client building --role public_user
timeout 2
start "main.py building, running on port 8018" python main.py --port 8018 --client building --role public_user
timeout 2
start "main.py building, running on port 8016" python main.py --port 8016 --client building --role public_user
timeout 2
start "main.py building, running on port 8014" python main.py --port 8014 --client building --role public_user
timeout 2
start "main.py community, running on port 8066" python main.py --port 8066 --client community --role owner
timeout 2
start "main.py community, running on port 8072" python main.py --port 8072 --client community --role owner
timeout 2
start "main.py community, running on port 8074" python main.py --port 8074 --client community --role owner
timeout 2
start "main.py community, running on port 8076" python main.py --port 8076 --client community --role owner
timeout 2
start "main.py community, running on port 8078" python main.py --port 8078 --client community --role owner
timeout 2
start "main.py community, running on port 8082" python main.py --port 8082 --client community --role owner
timeout 2
start "main.py community, running on port 8084" python main.py --port 8084 --client community --role owner
timeout 2
start "main.py community, running on port 8086" python main.py --port 8086 --client community --role owner
timeout 2
start "main.py community, running on port 8088" python main.py --port 8088 --client community --role owner
timeout 2
start "main.py community, running on port 8090" python main.py --port 8090 --client community --role owner
timeout 2
start "main.py dso, running on port 8012" python main.py --port 8012 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 8010" python main.py --port 8010 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9068" python main.py --port 9068 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9070" python main.py --port 9070 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9072" python main.py --port 9072 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9074" python main.py --port 9074 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9076" python main.py --port 9076 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9078" python main.py --port 9078 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9080" python main.py --port 9080 --client dso --role business_partner
timeout 2
start "main.py dso, running on port 9082" python main.py --port 9082 --client dso --role business_partner
timeout 2
start "main.py government, running on port 8070" python main.py --port 8070 --client government --role business_partner
ECHO All scripts are running...
PAUSE