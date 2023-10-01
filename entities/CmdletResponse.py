import asyncio
from json import dumps
from entities.Cmdlet import *
from configuration.Config import *
from exceptions.PSRExceptions import StreamTimeout, ProcessorException

class CmdletResponse():
    def __init__(self, command: dict) -> None:
        self.command = command
        self.task = asyncio.create_task(self.execute_on_processor())
        self.status = None
        self.reader = None
        self.writer = None
        self.timeout = command['ttl']

    async def validate(self) -> None:
        while(self.status == None):
            await asyncio.sleep(0.001)
            self.timeout -= 0.001

            if(self.timeout <= 0):
                self.task.cancel()
                raise StreamTimeout('Timed out waiting for stream status response.')

        if self.status == 1:
            raise ProcessorException('Too many busy.')

    async def get_length(self) -> int:
        # Read the length of the response
        data = await self.reader.read(16)
        return int(data.decode('utf-8'))
    
    async def get_content(self):
        while True:
            data = await self.reader.read(1024)

            if(not data):
                break

            yield data
        
        self.task.cancel()

    async def execute_on_processor(self):
        if(PLATFORM == 'Windows'):
            self.reader, self.writer = await asyncio.open_connection('localhost', 5000)
        else:
            self.reader, self.writer = await asyncio.open_unix_connection(INGESTER_UNIX_ADDRESS)

        message = dumps(self.command).encode('utf-8')
        self.writer.write(str(len(message)).zfill(8).encode('utf-8'))
        await self.writer.drain()
        self.writer.write(message)
        await self.writer.drain()
        data = await self.reader.read(1)
        self.status = int(data.decode('utf-8'))
  