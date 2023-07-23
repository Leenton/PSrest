from queue import Queue, Empty
import asyncio
from exceptions.PSRExceptions import PSRQueueException
from json import dumps,loads

class PSRestQueue():

    def __init__(self):
        self.queue = Queue()
        self.associated_queue = Queue()
        
    async def put(self, message: str, retry = 6)-> None: 
        tries = 1
        while(retry > tries):
            try:
                reader, writer = await asyncio.open_unix_connection('./PSRestQueue13')
                writer.write(message.encode('utf-8'))
                await writer.drain()
                break
            except Exception:
                retry += 1
                await asyncio.sleep(0.01 * retry)
        
        writer.close()

        if(retry == tries):
            raise PSRQueueException('Failed to send message to PSRestQueue, via unix socket.')

    async def receive_commands(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read()
        if(data):
            self.queue.put(data.decode('utf-8'))

    async def serve_associated(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            associated = self.associated_queue.get(False)
            writer.write(associated.encode('utf-8'))
            await writer.drain()
            writer.close()
        except Empty:
            writer.close()
        
    async def serve(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read()
        if(data):
            pid = (data.decode('utf-8'))
            while(True):
                try:
                    command = self.queue.get(False)
                    break
                except Empty:
                    await asyncio.sleep(0.001)

            self.associated_queue.put(dumps({'pid': pid, 'ticket': loads(command)['ticket']}))
            writer.write(command.encode('utf-8'))
            await writer.drain()
            writer.close()
    
    async def get(self) -> str:
        reader, writer = await asyncio.open_unix_connection('./PSRestQueue15')
        data = await reader.read()
        if(data):
            return data.decode('utf-8')
        else:
            raise PSRQueueException('Empty queue.')

    async def start_serving(self):
        server = await asyncio.start_unix_server(self.serve, './PSRestQueue14')
        async with server:
            await server.serve_forever()

    async def start_receive(self): 
        listener = await asyncio.start_unix_server(self.receive_commands, './PSRestQueue13')
        async with listener:
            await listener.serve_forever()

    async def start_serving_associated(self):
        server = await asyncio.start_unix_server(self.serve_associated, './PSRestQueue15')
        async with server:
            await server.serve_forever()

    async def start(self):
        serve = asyncio.create_task(self.start_serving())
        receive = asyncio.create_task(self.start_receive())
        associated = asyncio.create_task(self.start_serving_associated())

        await serve
        await receive
        await associated