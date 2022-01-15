import json

# open JSON file/read JSON file
f = open('actors_relation.json',)

# returns JSON object as a dictionary
data = json.load(f)
# Closing file
f.close()

# variable to store actors run command
batch = ''

# list of available ports
ports=[]
# generate 1000 ports between 3000 to 5000
for port in range(3000,5000):
    if (port % 2) == 0:
        ports.append(port)

# actor command format
cmd='start "main.py {3}, running on port {1}" python main.py --port {1} --client {0} --role {2} --id {3}\ntimeout 2\n'
# iterate json file (data), iterate main companies (wood cutter, transport)
for index, company in enumerate(data['forest']):
    company_id = company['actor']+str(index)
    # iterate companies in each company category, intances of one main company 
    for index,sub_company in enumerate(company['companies']):
        sub_company_id =  company_id+"-"+str(index)
        # pass values to cmd indexer mentioned on line 22 to map values
        batch += cmd.format(company['actor'], ports.pop(), sub_company['role'], sub_company_id)
              
batch = 'start "Registry Server" python registry_server.py\ntimeout 2\n' + batch
bat = open(r'auto_run.bat','w+')
bat.write(batch)
bat.close()
