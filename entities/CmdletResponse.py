import asyncio
from json import dumps
from .ProcessorConnection import ProcessorConnection
from errors import StreamTimeout, ProcessorException

class CmdletResponse():
    def __init__(self, command: dict) -> None:
        self.command = command
        self.timeout = command['ttl']
        self.reader: asyncio.StreamReader
        self.writer: asyncio.StreamWriter
 
    async def get_length(self) -> int:
        # Read the length of the response
        data = await self.reader.read(16)
        return int(data.decode('utf-8'))
    
    async def get_content(self):
        while True:
            data = await self.reader.read(4096)
            
            if(not data):
                break
            yield data

        self.writer.close()

    async def execute(self):
        self.reader, self.writer = await (ProcessorConnection()).connect()
            
        message = dumps(self.command).encode('utf-8')
        self.writer.write(b'e' + str(len(message)).zfill(8).encode('utf-8') + message)
        await self.writer.drain()

        try:
            status = await asyncio.wait_for(self.reader.read(1), timeout=self.timeout)
        except TimeoutError:
            raise StreamTimeout('Timed out waiting for stream status response.')

        if int(status.decode('utf-8')) == 1:
            raise ProcessorException('Too many busy.')
        
        return self