from datetime import datetime
from entities.PSTicket import PSTicket
from minio import Minio
from Config import * 
from time import sleep
from exceptions.PSRExceptions import ExpiredPSTicket

class PSResponseStorage():
    def __init__(self, server, access_key, secret_key) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.s3client = Minio(server, access_key, secret_key, secure=False)
    
    def store(self, ticket: PSTicket, response):
        self.s3client.put_object(S3BUCKET, ticket.id, response)
    
    async def get(self, ticket: PSTicket):
        while(ticket.expires > int(datetime.timestamp(datetime.now()))):
            try:
                return self.s3client.get_object(S3BUCKET, ticket.id)
            except Exception: 
                sleep(0.001)
        raise ExpiredPSTicket(ticket)
    
    async def delete(self, ticket: PSTicket) -> None:
        self.s3client.remove_object(S3BUCKET, ticket.id)
    
    def clear(self):
        while(True):
            objects = self.s3client.list_objects(S3BUCKET)
            try:
                oldest_object = min(objects, key=lambda obj: obj.last_modified)
                if(datetime.timestamp(oldest_object.last_modified) + 6000 < datetime.timestamp(datetime.now())):
                    self.s3client.remove_object(S3BUCKET, oldest_object.object_name)
                    #TODO: We should probably log the removal of this object?
                    sleep(0.01)
            except ValueError:
                sleep(1.00)
            except Exception as e:
                #TODO: We should probably log this some where? 
                print(e)
                sleep(1.00)
            