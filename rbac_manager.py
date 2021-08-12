#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# https://github.com/jackeyGao/simple-rbac
import rbac.acl
from time import perf_counter
from csv_log import CSVLogger
class RbacManager:
    def __init__(self):
        # list of clients
        self.clients = ["occupant", "household", "building", "community",  "dso", "government"]

        #self.clients1 = {'gov': 'government', 'dso': 'DSO', 'community': 'community', 'building': 'building1', 'household': 'building1-household1',
        #'occupant': 'building1-household1-occupant1'}
        #self.clients1_names = ", ".join(self.clients1)
        
        # business partners rules definition
        self.business_partners=[]
        self.business_partners.append(("community","dso"))
        self.business_partners.append(("community","government"))
        self.business_partners.append(("household","building"))
        self.business_partners.append(("occupant","building"))
        self.business_partners.append(("occupant","household"))
        self.business_partners.append(("occupant","community"))
        self.business_partners.append(("household","community"))

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

    # check if current role is valid to access block based on privacy type e.g user is allow to access public data only 
    def verify_privacy(self, client_role, privacy_type):
        if( (client_role == 'owner') or
            (client_role == 'business_partner' and privacy_type != 'private-data') or
            (client_role == 'public_user' and privacy_type == 'public-data')):
            print('Privacy validated')
            return True
        else:
            return False

     #def verify_partner_privacy(self, clients1, client_role, privacy_type):
        #for name in clients1: 
           # if 'community' == 'business_partner' and 'dso' == 'business_partner':
            #    return privacy_type != 'private-data'
            # elif 'community' == 'business_partner' and 'gov' == 'business_partner':
              #   return privacy_type != 'private-data'
            # elif 'household' == 'business_partner' and 'building' == 'business_partner':
              #   return privacy_type != 'private-data'
            # elif 'household' == 'business_partner' and 'occupant' == 'business_partner':
              #   return privacy_type != 'private-data'
            # elif 'occupant' == 'business_partner' and 'building' == 'business_partner':
              #   return privacy_type != 'private-data'
            # elif 'household' == 'business_partner' and 'community' == 'business_partner':
             #    return privacy_type != 'private-data'
            # elif 'occupant' == 'business_partner' and 'community' == 'business_partner':
              #   return privacy_type != 'private-data'
            # else:
              #   return False
    
    #verify_partner_privacy(community, business_partner, public_data)

    
    # check if current user is business partner with other user
    def check_business_partner(self, current_actor, other_actor):
        if((current_actor,other_actor) in self.business_partners):
            return True
        elif((other_actor, current_actor) in self.business_partners):
            return True
        else:
            return False


rbac = RbacManager()
if(rbac.check_business_partner('dso','community')):
    print("business partners")
else:
    print("not business partners")