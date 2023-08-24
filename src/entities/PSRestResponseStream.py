import asyncio
from os import unlink, remove

from configuration.Config import *
from processing.PSProcessor import PSProcessor
from entities.PSTicket import PSTicket
from exceptions.PSRExceptions import StreamTimeout

class PSRestResponseStream():
    def __init__(self, ticket: PSTicket, processor: PSProcessor) -> None:
        self.path: str = RESPONSE_DIR + f'/{ticket.id}'
        self.length = None
        self.timeout = ticket.ttl
        self.ticket = ticket
        self.processor = processor
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.task: asyncio.Task

    async def open(self):
        self.task = asyncio.create_task(self.start())

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(16)
        self.length = int(data.decode('utf-8'))
        self.reader = reader
        self.writer = writer

    async def get_length(self):
        while(self.length == None):
            await asyncio.sleep(0.001)
            self.timeout -= 0.001

            if(self.timeout <= 0):
                await self.close(True)
                raise StreamTimeout('Timed out waiting for stream length response.')

        return self.length

    async def read(self):
        while(self.length == None):
            await asyncio.sleep(0.005)
        
        while(self.reader == None and self.writer == None):
            await asyncio.sleep(0.001)
            self.timeout -= 0.001

            if(self.timeout <= 0):
                await self.close(True)
                raise StreamTimeout('Timed out waiting for stream data response.')

        while True:
            data = await self.reader.read(1024)

            if(not data):
                break

            yield data

        await self.processor.send_result({'ticket':self.ticket.serialise(), 'status': COMPETED})
        await self.close()
    
    async def start(self):
        try:
            server = await asyncio.start_unix_server(self.handle_connection, path=self.path, limit=1024*1024)

            async with server:
                await server.serve_forever()

        except asyncio.CancelledError:
            return

    async def close(self, failure: bool = False):
        self.task.cancel()
        unlink(self.path)

        if(failure):
            await self.processor.send_result({'ticket': self.ticket.id, 'status': FAILED, 'error': 'Stream timed out.'})