import asyncio

from configuration import INGESTER_ADDRESS, INGESTER_UNIX_ADDRESS, PLATFORM, PROCESSOR_HOST, PSREST_PORT

if (PLATFORM == 'Windows'):
    from socket import socket, AF_INET,  SOCK_STREAM
else:
    from socket import socket, AF_INET, AF_UNIX,  SOCK_STREAM

class ProcessorConnection():
    async def connect(self) -> tuple[asyncio.StreamReader,asyncio.StreamWriter]:
        if(PLATFORM == 'Windows'):
            # windows python doesn't support unix sockets natively, so we have to use a tcp socket.
            return await asyncio.open_connection(PROCESSOR_HOST, PSREST_PORT)
        else:
            # unix python supports unix sockets natively, so we can use them. 
            return await asyncio.open_unix_connection(INGESTER_UNIX_ADDRESS)
        
    def connect_sync(self) -> socket:
        if(PLATFORM == 'Windows'):
            soc = socket(AF_INET, SOCK_STREAM)
            soc.connect(INGESTER_ADDRESS)
        else:
            soc = socket(AF_UNIX, SOCK_STREAM)
            soc.connect(INGESTER_UNIX_ADDRESS)

        return soc