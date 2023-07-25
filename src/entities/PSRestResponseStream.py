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

    # def __init__(self, ticket : PSTicket):
    #     super().__init__()
    #     self._is_closed = False
    #     self.ticket = ticket

    # def __enter__(self):
    #     return self
    
    # def read(self):
    #     #make a socket connection to the ticket file
    #     soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    #     soc.bind(f'{RESPONSE_DIR}/{self.ticket}')
    #     soc.listen(1)
    #     conn, addr = soc.accept()
    #     data = conn.read()
    #     conn.close()
    #     soc.close()

    #     return data

    # def close(self):
    #     if not self._is_closed:
    #         self.response.close()
    #         self._is_closed = True
    #     super().close()

    # def __del__(self):
    #     self.close()

    