from datetime import datetime
from entities.PSTicket import PSTicket
from minio import Minio
from Config import * 
from time import sleep
from exceptions.PSRExceptions import ExpiredPSTicket

class PSResponseStorage():
    def __init__(self,) -> None:
        pass
    
    async def get(self, ticket: PSTicket):
        while(ticket.expires > int(datetime.timestamp(datetime.now()))):
            try:
                return self.s3client.get_object(S3BUCKET, ticket.id)
            except Exception: 
                sleep(0.001)
        raise ExpiredPSTicket(ticket)
    
    def clear(self):
        pass

    def delete(self, ticket: PSTicket):
        pass