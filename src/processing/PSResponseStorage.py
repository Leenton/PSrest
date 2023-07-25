from datetime import datetime
from entities.PSTicket import PSTicket
from minio import Minio
from Config import * 
from time import sleep
from exceptions.PSRExceptions import ExpiredPSTicket
import asyncio
from os.path import exists
class PSResponseStorage():
    def __init__(self,) -> None:
        pass
    
    async def get(self, ticket: PSTicket) -> str:
        '''Returns the file path to a json file containing the response of the command.'''
        while(ticket.expires > int(datetime.timestamp(datetime.now()))):
            try:
                #check if a directory exists for the ticket
                if(exists(f'{SIGNAL_DIR}/{ticket.id}')):
                    return f'{RESPONSE_DIR}/{ticket.id}'
                else:
                    asyncio.sleep(0.001)
            except Exception: 
                asyncio.sleep(0.001)
        raise ExpiredPSTicket(ticket)
