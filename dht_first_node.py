# pip install kademlia

import logging
import asyncio

from kademlia.network import Server

# logging start
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)
# logging end

#create loop object
loop = asyncio.get_event_loop()
loop.set_debug(True)

# create dht server
server = Server()

# pass dht server to loop object
loop.run_until_complete(server.listen(1111))

# run server
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
    loop.close()