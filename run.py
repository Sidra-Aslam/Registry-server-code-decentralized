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
cmd='start "main.py {3}, running on port {1}" python main.py --port {1} --client {0} --role {2} --id {3}\n'
# iterate json file (data)
for gov in data:
    batch += cmd.format(gov['actor'], ports.pop(), gov['role'], gov['id'])
    
    # create dso batch command 
    dso = gov['dso']
    batch += cmd.format(dso['actor'], ports.pop(), dso['role'], dso['id'])
    
    #create community batch command
    community=gov['dso']['community']
    batch += cmd.format(community['actor'], ports.pop(), community['role'], community['id'])
    
    # one community can have multiple buildings 
    # so iterate all buildings
    for building in community['buildings']:
        
        # create batch commant for each building in community
        batch += cmd.format(building['actor'], ports.pop(), building['role'], building['id'])

        # one building can have multiple house holds
        # so iterate each household in building
        for household in building['households']:

            batch += cmd.format(household['actor'], ports.pop(), household['role'], household['id'])

            for occupant in household['occupants']:
                batch += cmd.format(occupant['actor'], ports.pop(), occupant['role'], occupant['id'])
            

bat = open(r'auto_run.bat','w+')
bat.write(batch)
bat.close()

