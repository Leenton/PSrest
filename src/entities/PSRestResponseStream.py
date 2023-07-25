import io
import socket
from entities.PSTicket import PSTicket
from Config import *
import asyncio

class PSRestResponseStream():
    def __init__(self, ticket: PSTicket) -> None:
        self.ticket = ticket

    async def read(self):
        reader, writer = await asyncio.open_unix_connection(f'{RESPONSE_DIR}/{self.ticket.id}')
        while(True):
            data = await reader.readuntil(f'{self.ticket.id}'.encode('utf-8'))
            if(data):
                yield data
            else:
                break
        yield None