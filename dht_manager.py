
class DhtManager:
    
    def __init__(self):
        self.dht = {}
        
    def get_value(self, key):
        if key in self.dht.keys():
            return self.dht[key]
        else:
            return None

    def set_value(self, key, value):
        if key in self.dht.keys():
            self.dht[key] = value
            print('Data modified against pointer: ' + key)

        # if key does not exists on dht then store new value
        else:
            print('Data stored against pointer: ' + key)
            self.dht[key] = value

    # delete value to dht server
    def delete_value(self, key):
        if key in self.dht.keys():
            self.dht[key] = 'DELETED'
            print("key '"+key+"' deleted")
        else:
            print('Key does not exists')