
import asyncio
import socket
from os import unlink
from math import factorial

from configuration.Config import *
from processing.PSProcessor import PSProcessor
from psrlogging.PSRestLogger import Logger
from psrlogging.LogMessage import LogMessage
from psrlogging.LogLevel import LogLevel
from psrlogging.LogCode import LogCode
from entities.PSTicket import PSTicket

class PSRestResponseStream():
    def __init__(self, ticket: PSTicket, processor: PSProcessor, logger: Logger) -> None:
        self.ticket = ticket
        self.processor = processor
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

        self.processor.send_result({'ticket':self.ticket.serialise(), 'status': COMPETED})

        #delete the file when we are done with it
        tries = 1
        backoff = 0.001
        while(tries <= 5):
            try:
                unlink(RESPONSE_DIR + f'./{self.ticket.id}')
                break
            except FileNotFoundError:
                tries += 1
                await asyncio.sleep(backoff*(factorial(tries)))
                break
        
        if(tries >= 5):
            self.logger.log(LogMessage(message=f'Failed to delete {self.ticket.id} after 5 tries.', level=LogLevel.ERROR, code=LogCode.System))