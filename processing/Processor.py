from time import sleep
from queue import Queue
import asyncio
from json import dumps, loads
from datetime import datetime
from uuid import uuid4
from collections import deque

# Internal imports
from configuration.Config import *
from entities.Ticket import Ticket
from entities.Process import Process, ProcessStatus
from entities.ProcessResponse import ProcessResponse

class Processor():
    def __init__(self):
        self.queue: Queue[Ticket] = Queue()
        self.accumulator = asyncio.Queue()
        self.processes: dict[str, Process] = {}
        self.responses: dict[str, ProcessResponse]  = {}
        self.schedule: deque[Ticket] = deque([])
        self.this_tick = datetime.timestamp(datetime.now())
        self.aceepting_requests = True
        self.oldest_free_process: str = ''

    async def execute_command(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(32)
        if(data):
            pid = (data.decode('utf-8'))
            self.processes[pid].status = ProcessStatus.FREE
            self.processes[pid].last_seen = self.this_tick
            self.processes[pid].current_ticket = None
            self.processes[pid].current_ticket_expiry = None
            
            # TODO: if we end up writing double the amount of data to the pipe, switch back to using a queue
            ticket: Ticket = await self.accumulator.get()
            ticket.pid = pid

            self.processes[pid].status = ProcessStatus.BUSY
            self.processes[pid].last_seen = self.this_tick
            self.processes[pid].current_ticket = ticket.id
            self.processes[pid].current_ticket_expiry = ticket.expires

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


    async def accept_command(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # TODO: SUPPORT READING DIFFERENT KINDS OF COMMANDS LIKE KILL REQUESTS
    
        data = await reader.read(8)
        if(data):
            data = await reader.read(int(data.decode('utf-8')))
            # Get the command from the queue and generate a ticket to track it's execution
            command = loads(data.decode('utf-8'))
            ticket = Ticket(command)
            self.queue.put(ticket)
        
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
                
                if(ticket.expires < self.this_tick):
                    writer.close()
                
                else:
                    # TODO: Exponential backoff here to prevent busy waiting
                    await asyncio.sleep(0.001)

    async def return_response(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(32)
        if(data):
            ticket = (data.decode('utf-8'))
            self.responses[ticket] = ProcessResponse(COMPETED, (await reader.read(16)), reader, writer)      
    
    async def start_executing(self):
        if(PLATFORM == 'Windows'):
            server = await asyncio.start_server(self.execute_command, 'localhost', 5000)
            async with server:
                await server.serve_forever()
        else:
            server = await asyncio.start_unix_server(self.execute_command, DISTRIBUTOR_UNIX_ADDRESS)
            async with server:
                await server.serve_forever()

    async def start_accepting(self):
        if(PLATFORM == 'Windows'):
            server = await asyncio.start_server(self.accept_command, 'localhost', 5001)
            async with server:
                await server.serve_forever()
        else:
            server = await asyncio.start_unix_server(self.accept_command, INGESTER_UNIX_ADDRESS)
            async with server:
                await server.serve_forever()

    async def start_responding(self):
        if(PLATFORM == 'Windows'):
            server = await asyncio.start_server(self.return_response, 'localhost', 5002)
            async with server:
                await server.serve_forever()
        else:
            server = await asyncio.start_unix_server(self.return_response, RESPONDER_UNIX_ADDRESS)
            async with server:
                await server.serve_forever()

    def kill(self, pid: str):
        self.processes[pid].terminate()
        del self.processes[pid]

    def spawn_process(self):
        pid = uuid4().hex
        self.processes[pid] = Process(pid, self.this_tick, self.this_tick)
        
    def clear_schedule(self):
        new_schedule: deque[Ticket] = deque([])
        try:
            while(True):
                ticket = self.schedule.popleft()
                if(ticket.expires > self.this_tick):
                    new_schedule.append(ticket)
                else:
                    self.kill(ticket.pid)

        except IndexError:
            pass

        self.schedule = new_schedule

    def accept_new_requests(self):
        try:
            ticket = self.queue.get_nowait()

            if(self.aceepting_requests):
                self.schedule.append(ticket)
            else:
                self.responses[ticket.id] = ProcessResponse(FAILED, 0)
        except Exception:
            pass

    async def execute_from_schedule(self)-> None:
        # Itterate over the dictionary of processes
        oldest_free_process: float | None = None
        for pid, process in self.processes.items():
            if(process.current_ticket_expiry and process.current_ticket_expiry < self.this_tick):
                self.kill(pid)

            elif(process.status == ProcessStatus.FREE):
                try:
                    await self.accumulator.put(self.schedule.popleft())
                except Exception:
                    pass

                if(not oldest_free_process):
                    oldest_free_process = pid
                else:
                    if(self.processes[pid].status == ProcessStatus.FREE and process.last_seen < self.processes[oldest_free_process].last_seen):
                        oldest_free_process = pid

    async def scale_up(self) -> bool:
        if(len(self.processes) < PS_PROCESSORS):
            self.spawn_process()
            return True
        
        if(len(self.processes) < MAX_PROCESSES):
            try:
                if (self.schedule[0].created < self.this_tick - PROCESSOR_SPIN_UP_PERIOD) :
                    self.spawn_process()
                    return True
            except Exception:
                pass

        return False
        
    def scale_down(self):
        if(len(self.processes) > PS_PROCESSORS):
            if(self.oldest_free_process and self.processes[self.oldest_free_process].last_seen < self.this_tick - PROCESSOR_SPIN_DOWN_PERIOD ):
                self.kill(self.oldest_free_process)

    async def sleep(self):
        await asyncio.sleep(0.001)

    async def run(self):
        while len(self.processes) < PS_PROCESSORS:
            self.spawn_process()

        while True:
            self.this_tick = datetime.timestamp(datetime.now())
            self.clear_schedule()
            self.accept_new_requests()
            await self.execute_from_schedule() # Execute the commands in the schedule

            if(not await self.scale_up()):
                self.scale_down()

            await self.sleep()

    async def start(self):
        #Start listening for commands and also start giving commands to the powershell processes
        accept_commands = asyncio.create_task(self.start_accepting())
        execute_command = asyncio.create_task(self.start_executing())
        return_response = asyncio.create_task(self.start_responding())
        sleep(0.5)
        run_processor = asyncio.create_task(self.run())
        
        
        await accept_commands
        await execute_command
        await return_response
        await run_processor

def start_processor():
    try:
        processor = Processor()
        asyncio.run(processor.start())

    except KeyboardInterrupt:
        exit(0)
