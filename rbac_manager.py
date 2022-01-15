#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# https://github.com/jackeyGao/simple-rbac
import rbac.acl
from time import perf_counter
from csv_log import CSVLogger
class RbacManager:
    def __init__(self):
        # list of clients
        self.clients = ["wood_cutting", "transport", "warehouse_manager", "Furniture_assembly",  "Furniture_shop", "customer"]
        
        # business partners rules definition
        self.business_partners=[]
        self.business_partners.append(("wood_cutting","transport"))
        self.business_partners.append(("transport","warehouse_manager"))
        self.business_partners.append(("warehouse_manager","Furniture_assembly"))
        self.business_partners.append(("Furniture_assembly","Furniture_shop"))
        self.business_partners.append(("Furniture_shop","customer"))
        
        self.client_names = ", ".join(self.clients)

        # create rbac object of RBAC library
        self.acl = rbac.acl.Registry()
        # define roles
        self.acl.add_role('owner')
        self.acl.add_role('business_partner')
        self.acl.add_role('public_user')

        # define resources
        self.acl.add_resource("blockchain")
        
        # define allowed permissions
        self.acl.allow('owner', 'read', 'blockchain')
        self.acl.allow('owner', 'write', 'blockchain')
        self.acl.allow('owner', 'update', 'blockchain')
        self.acl.allow('owner', 'delete', 'blockchain')
        self.acl.allow('owner', 'share', 'blockchain')
        
        self.acl.allow('business_partner', 'read', 'blockchain')
        self.acl.allow('public_user', 'read', 'blockchain')


    # this method will be used to verify permission of actions (delete,write, update, read)
    def verify_permission(self, role, operation, resource):
        start_time = perf_counter()
        result = self.acl.is_allowed(role, operation, resource) is not None
        self.permission_time = (perf_counter()-start_time)
        CSVLogger.timeObj['RbacTime'] = self.permission_time
        
        print("\nTime to verify permission:", format(self.permission_time, '.8f'))
        return result
        
    # this method will be used to authenticate role if it exists
    def authenticate(self, client, role):
        return client in self.clients and self.acl._roles.get(role) is not None

    # check if current user is business partner with other user
    def check_business_partner(self, current_actor, other_actor):
        if((current_actor,other_actor) in self.business_partners):
            return True
        elif((other_actor, current_actor) in self.business_partners):
            return True
        # when same actor reads the data (data owner and requester is the same)
        elif(other_actor == current_actor):
            return True
        else:
            return False


# rbac = RbacManager()
# if(rbac.check_business_partner('dso','government')):
#     print("business partners")
# else:
#     print("not business partners")