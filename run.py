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
# iterate json file (data)
for index, gov in enumerate(data):
    gov_id = gov['actor']+str(index)
    batch += cmd.format(gov['actor'], ports.pop(), gov['role'], gov_id)
    
    if 'dso' in gov:
        # create dso batch command 
        dso = gov['dso']
        dso_id = gov_id+"-"+dso['actor']
        batch += cmd.format(dso['actor'], ports.pop(), dso['role'], dso_id)
        if 'community' in dso:
            #create community batch command
            community = dso['community']
            community_id = gov_id+"-"+community['actor']
            
            batch += cmd.format(community['actor'], ports.pop(), community['role'], community_id)
            
            if 'buildings' in community:
                # one community can have multiple buildings 
                # so iterate all buildings
                for index,building in enumerate(community['buildings']):
                    building_id = gov_id+"-"+building['actor']+str(index)
                    # create batch commant for each building in community
                    batch += cmd.format(building['actor'], ports.pop(), building['role'], building_id)

                    if 'households' in building:
                        # one building can have multiple house holds
                        # so iterate each household in building
                        for index,household in enumerate(building['households']):
                            household_id = building_id+"-"+household['actor']+str(index)

                            batch += cmd.format(household['actor'], ports.pop(), household['role'], household_id)
                            if 'occupants' in household:
                                for index, occupant in enumerate(household['occupants']):
                                    occupant_id = household_id+"-"+occupant['actor']+str(index)
                                
                                    batch += cmd.format(occupant['actor'], ports.pop(), occupant['role'], occupant_id)
                            
batch = 'start "Registry Server" python registry_server.py\ntimeout 2\n' + batch
bat = open(r'auto_run.bat','w+')
bat.write(batch)
bat.close()

