# https://github.com/jackeyGao/simple-rbac
import rbac.acl
import time

class RbacManager:
    def __init__(self):
        # list of clients
        self.clients = ["wood_cutter", "transporter", "warehouse_storage", "furniture_assembly",  "furniture_shop", "customer"]
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
        start_time = time.time()
        result = self.acl.is_allowed(role, operation, resource) is not None
        print("\nTime to verify permission:", (time.time()-start_time))
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