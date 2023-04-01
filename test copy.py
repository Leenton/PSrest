import asyncio
# import nats # pip install nats.py
# from datetime import datetime
# from time import sleep

# async def main():
#     # Connect to NATS!
    

#     # Simple publisher and async subscriber via coroutine.
#     nc = await nats.connect("localhost:4222")
    
#     while(True):
#         await nc.publish("test", b'Hello')
#         print("Sent")

    
#     # msg = await sub.next_msg(60)
#     # now = datetime.now()
#     # count = 0
    
#     # while(True):
#     #     msg = await sub.next_msg(5)
#     #     print("Received:", msg.data)
#     #     count += 1
#     #     if(count == 1000):
#     #         break

#     # print(now)
#     # print(datetime.now())
        

# if __name__ == '__main__':
#     asyncio.run(main())



# # import asyncio
# # import nats

# # async def main():
# #     # Connect to NATS!
# #     nc = await nats.connect("localhost:4222")

# #     # Receive messages on 'foo'
# #     sub = await nc.subscribe("test")

# #     # Process a message
# #     msg = await sub.next_msg(60)
# #     print("Received:", msg)

# # if __name__ == '__main__':
# #     asyncio.run(main())


from datetime import datetime
from minio import Minio
from time import sleep
class PSResponseStorage():
    def __init__(self, server = None, access_key = None, secret_key = None) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.s3client = Minio(server, access_key, secret_key, secure=False)
    
    # def store(self, ticket: PSTicket, response):
    #     self.s3client.put_object(S3BUCKET, ticket.id, response)
    
    async def get(self, ticket: str):
        # while(ticket.expires > int(datetime.timestamp(datetime.now()))):
        #     try:
        #         self.s3client.fget_object(S3BUCKET, ticket.id, f'/tmp/{ticket.id}')
        #     except: 
        #         sleep(0.001)
        #add the ticket onto the delete queue incase a response is received after the ticket expires
        
        temp = self.s3client.get_object('test', ticket)

        # self.s3client.remove_object('test', ticket)
        # raise Exception('Ticket expired before response was received')
        print(temp)
    
    # def delete(self, ticket: PSTicket):
    #     del self.responses[ticket.id]
    
    # def get_all(self):
    #     return self.responses
    
    # def clear_old_responses(self):
    #     while(True):
    #         # Get the list of objects in the bucket.
    #         objects = self.s3client.list_objects(S3BUCKET)

    #         # If there are no objects in the bucket, return False.
    #         if(objects):
    #             oldest_object = min(objects, key=lambda obj: obj.last_modified)
    #             if(datetime.timestamp(oldest_object.last_modified) + 6000 < datetime.timestamp(datetime.now())):
    #                 self.s3client.remove_object(S3BUCKET, oldest_object.object_name)


responsestore = PSResponseStorage('localhost:9000', 'mcmTU4zXs9f22hu9', 'AYMGmvCZcGq5w1rW8eLIYXfx525N8Fdy')
data = asyncio.run(responsestore.get('Docker.dmg'))

