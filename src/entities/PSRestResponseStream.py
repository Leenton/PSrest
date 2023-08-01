from entities.PSTicket import PSTicket
from Config import *
import socket
import os
import asyncio

class PSRestResponseStream():
    def __init__(self, ticket: PSTicket) -> None:
        self.ticket = ticket
        soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        soc.bind(RESPONSE_DIR + f'/{self.ticket.id}')
        soc.listen(1)
        soc.settimeout(ticket.ttl)
        connection, return_address = soc.accept()
        data = connection.recv(16)
        self.length = int(data.decode('utf-8'))
        self.connection = connection
        self.soc = soc

    async def read(self):
        while True:
            data = self.connection.recv(1024)
            if(not data):
                break
            yield data
        self.connection.close()
        self.soc.close()

        #delete the file when we are done with it
        tries = 1
        backoff = 0.001
        while(tries > 8):
            try:
                os.remove(RESPONSE_DIR + f'./{self.ticket}')
                break
            except FileNotFoundError:
                tries += 1
                await asyncio.sleep(backoff*tries)
                break