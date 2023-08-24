from falcon.asgi import App
import uvicorn
from time import sleep
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_403, HTTP_408, HTTP_500

from threading import Thread
import asyncio
from os import unlink, remove
from configuration.Config import *
from processing.PSProcessor import PSProcessor
from entities.PSTicket import PSTicket
from exceptions.PSRExceptions import StreamTimeout



class PSRestResponseStream():
    def __init__(self) -> None:
        self.path: str = './test'
        self.length = None
        self.timeout = 20
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.task: asyncio.Task

    async def open(self):
        self.task = asyncio.create_task(self.start(), name='PSRestResponseStream')
        print(f'Opened task for ticket')

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        print(f'Handling connection for ticket')
        print(f'Getting length for ticket')
        data = await reader.read(16)
        print(data)
        self.length = int(data.decode('utf-8'))
        print(f'Got length for ticket')
        self.reader = reader
        self.writer = writer

    async def get_length(self):
        print(f'Getting length for ticket')
        tasks = asyncio.all_tasks()
        for task in tasks:
            print(task.get_name())

        while(self.length == None):
            await asyncio.sleep(0.001)
            self.timeout -= 0.001

            if(self.timeout <= 0):
                await self.close(True)
                raise Exception('Timed out waiting for stream length response.')
        print(f'Got length for ticket in get length method')
        return self.length

    async def read(self):
        while(self.length == None):
            await asyncio.sleep(0.001)
        
        while(self.reader == None and self.writer == None):
            await asyncio.sleep(0.001)
            self.timeout -= 0.001

            if(self.timeout <= 0):
                await self.close(True)
                raise Exception('Timed out waiting for stream data response.')

        while True:
            data = await self.reader.read(1024)
            if(not data):
                break
            yield data

        await self.close()
    
    async def start(self):
        try:
            server = await asyncio.start_unix_server(self.handle_connection, self.path)
            async with server:
                print(f'Serving stream for ticket')
                await server.serve_forever()
        except asyncio.CancelledError as e:
            return
            
            
    async def close(self, failure: bool = False):
        unlink(self.path)
        self.task.cancel()
        if(failure):
            print('Stream failed to complete.')


class Test(object):
    def __init__(self) -> None:
        pass

    async def on_post(self, req, resp):
        resp.content_type = 'application/json'
        resp.status = HTTP_200
        
        try:
            stream = PSRestResponseStream()
            await stream.open()
            resp.content_length = await stream.get_length()
            resp.stream = stream.read()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    PSRest = App()
    PSRest.add_route('/run', Test()) #Page to run commands
    uvicorn.run(PSRest, host='0.0.0.0', port=80, log_level='info')