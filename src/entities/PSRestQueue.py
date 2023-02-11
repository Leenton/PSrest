# from queue import Queue
import rsa
import nats

def load_private_key():
    with open('keys/private.pem', 'rb') as p:
        return rsa.PrivateKey.load_pkcs1(p.read())

class PSRestQueue():

    def __init__(self, private_key = load_private_key()):
        self.private_key = private_key
        self.nats = None
        
    async def put(self, channel: str, message: str)-> None: 
        nc = await nats.connect("localhost:4222")
        await nc.publish(channel, self.encypt(message))
        await nc.flush()
        await nc.close()

    def encypt(self, message: str):
        data = rsa.encrypt(message.encode('utf-8'), self.private_key)
        return data

    def hash(self, channel: str):
        return channel
