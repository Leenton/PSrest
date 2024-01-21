from json import loads, dumps
import asyncio
from queue import Queue
from configuration import (
    COMPETED,
    INGESTER_UNIX_ADDRESS,
    PLATFORM,
    PROCESSOR_HOST,
    PSREST_PORT
)
from entities import (
    Ticket,
    Process,
    ProcessStatus,
    ProcessResponse,
    Clock
)
from .SnapshotInterupter import *

class IORouter():
    def __init__(
            self,
            processes: dict[str, Process],
            responses: dict[str, ProcessResponse],
            snapshot_buffer: asyncio.Queue[bytes],
            clock: Clock,
            ticket_queue: Queue[Ticket],
            accumulator: asyncio.Queue[Ticket],
            snapshot_interupter: SnapshotInterupter
        ) -> None:
        self.processes: dict[str, Process] = processes
        self.responses: dict[str, ProcessResponse] = responses
        self.snapshot_buffer: asyncio.Queue[bytes] = snapshot_buffer
        self.clock: Clock = clock
        self.ticket_queue: Queue[Ticket] = ticket_queue
        self.accumulator: asyncio.Queue[Ticket] = accumulator
        self.snapshot_interupter: SnapshotInterupter = snapshot_interupter

    async def io_hanlder(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        command = await reader.read(1)
        match command:
            case b'i':
                await self.request_command(reader, writer)
            case b'o':
                await self.store_response(reader, writer)
            case b'e':
                await self.get_response(reader, writer)
            case b's':
                await self.get_shell_count(reader, writer)
            case b'p':
                await self.get_processes(reader, writer)
            case b'k':
                await self.kill_process(reader, writer)
            case b'r':
                await self.remove_ticket(reader, writer)
            case _:
                writer.close()

    async def request_command(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(32)
        if(data):
            pid = (data.decode('utf-8'))
            self.processes[pid].status = ProcessStatus.FREE
            self.processes[pid].last_seen = self.clock.now
            self.processes[pid].current_ticket = None

            ticket: Ticket = await self.accumulator.get()
            ticket.pid = pid

            self.processes[pid].status = ProcessStatus.BUSY
            self.processes[pid].last_seen = self.clock.now
            self.processes[pid].current_ticket = ticket

            command = dumps({
                'Command': ticket.command['command'],
                'Ticket': ticket.id,
                'Depth': ticket.command['depth']
            }).encode('utf-8')
            
            # Left pad with 0 until its 16 bytes in length
            writer.write(str(len(command)).zfill(16).encode('utf-8'))
            await writer.drain()
            writer.write(command)
            await writer.drain()
        
        writer.close()

    async def store_response(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(32)
        if(data):
            ticket = (data.decode('utf-8'))
            self.responses[ticket] = ProcessResponse(COMPETED, (await reader.read(16)), reader, writer)

    async def get_response(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(8)
        if(data):
            data = await reader.read(int(data.decode('utf-8')))
            # Get the command from the queue and generate a ticket to track it's execution
            command = loads(data.decode('utf-8'))
            ticket = Ticket(command)
            self.ticket_queue.put(ticket)
        
            # Wait for the response to be returned
            while(True):
                if(ticket.id in self.responses):
                    response = self.responses.pop(ticket.id)
                    # Return the status of the response
                    if(response.status == 0):
                        writer.write('1'.encode('utf-8'))
                        await writer.drain()
                    else:
                        writer.write('0'.encode('utf-8'))
                        await writer.drain()

                        # Return the content length of the response
                        writer.write(response.length)
                        await writer.drain()

                        # Return the content of the response
                        while(True):
                            data = await response.reader.read(1024)
                            if(not data):
                                break
                            writer.write(data)
                            await writer.drain()
                        
                    response.writer.close()
                    writer.close()
                    break
                
                if(ticket.expiry < self.clock.now):
                    writer.write('2'.encode('utf-8'))
                    await writer.drain()
                    writer.close()
                    break
                
                else:
                    # TODO: Exponential backoff here to prevent busy waiting
                    await asyncio.sleep(0.001)

    async def get_shell_count(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(str(len(self.processes)).encode('utf-8'))
        await writer.drain()
        writer.close()

    async def get_processes(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while(self.snapshot_interupter.state != SnapshotState.IDLE):
            asyncio.sleep(0.005)

        try:   
            self.snapshot_interupter.state = SnapshotState.REQUESTING
            writer.write((await self.snapshot_buffer.get()))
            await writer.drain()
            writer.close()
        except:
            pass
        
        self.snapshot_interupter.state = SnapshotState.IDLE

    async def kill_process(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        pass

    async def remove_ticket(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        pass

    async def route(self):
        if(PLATFORM == 'Windows'):
            server = await asyncio.start_server(self.io_hanlder, PROCESSOR_HOST, PSREST_PORT)
            async with server:
                await server.serve_forever()
        else:
            server = await asyncio.start_unix_server(self.io_hanlder, INGESTER_UNIX_ADDRESS)
            async with server:
                await server.serve_forever()