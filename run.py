from owlready2 import *

onto = get_ontology("./AccessControl.owl").load()

# variable to store actors run command
batch = ''

# list of available ports
ports=[]
# generate 1000 ports between 3000 to 5000
for port in range(3000,5000):
    if (port % 2) == 0:
        ports.append(port)

# actor command format
cmd='start "main.py {0} - {2}, running on port {1}" python main.py --port {1} --client {0} --role {2}\ntimeout 2\n'

# iterate all actor instances from ontology
for actor in onto.Actor.instances():
    # create command for actor based on actor name and role
    batch += cmd.format(actor.name, ports.pop(), actor.hasRole[0].name)
    
batch = 'start "Registry Server" python registry_server.py\ntimeout 2\n' + batch
bat = open(r'auto_run.bat','w+')
bat.write(batch)
bat.close()
