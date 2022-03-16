from owlready2 import *

# This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# https://owlready2.readthedocs.io/en/latest/install.html
import rbac.acl
from time import perf_counter
from csv_log import CSVLogger


class AccessControlOntologyManager:
    def __init__(self):
        # load ontology file 'AccessControl.owl'
        self.onto = get_ontology("./AccessControl.owl").load()

        # start reasoner to verify that ontology 'AccessControl.owl' file is consistent
        sync_reasoner()

        # if there is any inconsistent classes found then print error
        if(len(list(self.onto.inconsistent_classes())) > 0):
            print(list(self.onto.inconsistent_classes()))
            print("Above classes are inconsistent")
        else:
            # list of actors / individuals
            self.actors = list(self.onto.Actor.instances())
            self.roles = list(self.onto.Role.instances())

    # method to return role of any actor
    def get_actor_role(self, actor):
        # find  actor (i.e Alice, Bob) by name from ontology actor list and return role
        actor = next(c for c in self.actors if c.name == actor)
        if(actor != None and len(actor.hasRole) > 0):
            return actor.hasRole[0].name
        else:
            return None

    # method to return allowed parameters for any actor role
    def get_role_resources(self, role_name, permission):
        # find  actor (i.e Alice, Bob) by name from ontology
        ontology_role = next(r for r in self.roles if r.name == role_name)
        if(ontology_role != None):
            
            if permission == 'get':
                parameters = list(ontology_role.hasGetPermission)
            elif permission == 'post':
                parameters = list(ontology_role.hasPostPermission)
            elif permission == 'put':
                parameters = list(ontology_role.hasPermission)
            elif permission == 'delete':
                parameters = list(ontology_role.hasGetPermission)

            resources = {'Product_Id':''}
            for resource in parameters:
                resources[resource.name] = ''
            print(role_name + ' resources for '+ permission +':')
            print(resources)
            return resources
        else:
            return {}

        

    # this method is used to authenticate actor and his role from ontology by using hasRole property
    def authenticate(self, actor, role):
        # find current actor (i.e Alice, Bob) by name from ontology actor list
        actor = next(c for c in self.actors if c.name == actor)
        # then authenticate the role of the found actor
        if(actor != None and len(actor.hasRole) > 0 and actor.hasRole[0].name == role):
            # save/return current actor name and role
            self.current_actor = actor
            self.current_role = actor.hasRole[0]
            return True
        else:
            return False

    # this method is used to verify role level permission of verbs (get, post, put, delete) from ontology
    def verify_class_rules(self, permission):
        start_time = perf_counter()

        result = False
        if self.current_actor is not None:
            if permission == 'get':
                result = len(self.current_role.hasGetPermission) > 0
            elif permission == 'post':
                result = len(self.current_role.hasPostPermission) > 0 
            elif permission == 'put':
                result = len(self.current_role.hasPutPermission) > 0
            elif permission == 'delete':
                result = len(self.current_role.hasDeletePermission) > 0

        self.permission_time = (perf_counter()-start_time)
        CSVLogger.timeObj['RbacTime'] = self.permission_time

        print("\nTime to verify permission:",
              format(self.permission_time, '.8f'))
        return result

    # this method is used to verify individual level permission of verbs (get, post, put, delete) from ontology
    def verify_individual_rules(self, permission):
        start_time = perf_counter()

        result = False
        if self.current_actor is not None:
            if permission == 'get':
                result = len(self.current_actor.hasGetPermission) > 0
            elif permission == 'post':
                result = len(self.current_actor.hasPostPermission) > 0
            elif permission == 'put':
                result = len(self.current_actor.hasPutPermission) > 0
            elif permission == 'delete':
                result = len(self.current_actor.hasDeletePermission) > 0

        self.permission_time = (perf_counter()-start_time)
        CSVLogger.timeObj['RbacTime'] = self.permission_time

        print("\nTime to verify permission:",
              format(self.permission_time, '.8f'))
        return result

    # check if current actor is business partner with other actor using ontology
    def check_business_partner(self, other_actor) -> bool:
        # this condition checks if owner reads his own data so we are check if current actor and other actor is same
        if self.current_actor.name == other_actor:
            return True
        # this condition checks if current actor is business partner with other actor
        elif self.current_actor is not None and len(self.current_actor.hasBusinessPartner) > 0:
            business_partner = [
                c for c in self.current_actor.hasBusinessPartner if c.name == other_actor]
            # return true if any business partner found
            return len(business_partner) > 0
        else:
            return False
