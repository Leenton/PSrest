from queue import Queue, Empty
import asyncio
from exceptions.PSRExceptions import PSRQueueException
from json import dumps,loads
from configuration.Config import *
from time import sleep
import socket
class PSRestQueue():

    def __init__(self):
        self.queue = Queue()
        self.associated_queue = Queue()
    
    async def put(self, message: str)-> None: 
        'Put a message on the queue to be distributed to a free PSProcessor.'

        reader, writer = await  asyncio.open_unix_connection(PSRESTQUEUE_PUT)
        writer.write(message.encode('utf-8'))
        await writer.drain()
        writer.close()

    
    def get(self) -> str: 
        soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        soc.connect(PSRESTQUEUE_GET)
        data = soc.recv(512).decode('utf-8')
        soc.close()

        if(data):
            return data
        else:
            return dumps({'pid': None, 'ticket': None})

    async def receive_commands(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        ''' Listens for commands from PSRESTQUEUE_PUT and puts them on the queue'''
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
        data = await reader.read(32)
        if(data):
            pid = (data.decode('utf-8'))

            while(True):
                try:
                    command: str = self.queue.get(False)
                    break
                except Empty:
                    await asyncio.sleep(0.001)

            self.associated_queue.put(dumps({'pid': pid, 'ticket': loads(command)['Ticket']}))
            command = command.encode('utf-8')
            length = len(command)
            
            #left pad with 0 until its 16 bytes in length
            writer.write(str(length).zfill(16).encode('utf-8'))
            await writer.drain()
            writer.write(command)
            await writer.drain()
            writer.close()
    
    async def start_serving(self):
        server = await asyncio.start_unix_server(self.serve, PSRESTQUEUE_SRV)
        async with server:
            await server.serve_forever()

    async def start_receive(self): 
        listener = await asyncio.start_unix_server(self.receive_commands, PSRESTQUEUE_PUT)
        async with listener:
            await listener.serve_forever()

    async def start_serving_associated(self):
        server = await asyncio.start_unix_server(self.serve_associated, PSRESTQUEUE_GET)
        async with server:
            await server.serve_forever()

    async def start(self):
        #Serves the Individual PSProcessors via global unix socket
        serve = asyncio.create_task(self.start_serving())

        #Receives commands from async requests generated by falcon and puts them into a queue
        #That is then served to the PSProcessors
        receive = asyncio.create_task(self.start_receive())

        #Alerts the Processor/Scheduler who picked up what from the queue
        associated = asyncio.create_task(self.start_serving_associated())


        await serve
        await receive
        await associated

def serve_queue():
    queue = PSRestQueue()
    asyncio.run(queue.start())