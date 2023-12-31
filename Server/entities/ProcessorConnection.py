import asyncio
from socket import socket, AF_INET, AF_UNIX,  SOCK_STREAM
from configuration import INGESTER_ADDRESS, INGESTER_UNIX_ADDRESS, PLATFORM

class ProcessorConnection():
    async def connect(self) -> tuple[asyncio.StreamReader,asyncio.StreamWriter]:
        if(PLATFORM == 'Windows'):
            return await asyncio.open_connection('localhost', 5000)
        else:
            return await asyncio.open_unix_connection(INGESTER_UNIX_ADDRESS)
        
    def connect_sync(self) -> socket:
        if(PLATFORM == 'Windows'):
            soc = socket(AF_INET, SOCK_STREAM)
            soc.connect(INGESTER_ADDRESS)
        else:
            soc = socket(AF_UNIX, SOCK_STREAM)
            soc.connect(INGESTER_UNIX_ADDRESS)

        return soc