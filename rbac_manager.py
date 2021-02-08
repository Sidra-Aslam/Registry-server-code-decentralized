# https://github.com/jackeyGao/simple-rbac
import rbac.acl

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
        
    # this method will be used to verify permission
    def verify_permission(self, role, operation, resource):
        return self.acl.is_allowed(role, operation, resource) is not None

    # this method will be used to authenticate role if it exists
    def authenticate(self, client, role):
        return client in self.clients and self.acl._roles.get(role) is not None