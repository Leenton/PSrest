from multiprocessing import Process, active_children, Queue
import subprocess
from uuid import uuid4
# from entities.PSTicket import PSTicket
# from entities.Cmdlet import Cmdlet 
# from entities.PSRestQueue import PSRestQueue
# import json 
# from exceptions.PSRExceptions import ProcessorException
import sqlite3
# from datetime import datetime
# from Config import PS_PROCESSORS, RESPONSE_DIR, PSRESTQUEUE_PUT
from threading import Thread
from time import sleep
PS_PROCESSORS = 4
RESPONSE_DIR = './tmp/resp'
PSRESTQUEUE_PUT = './tmp/5a682fbbe1bc487793d55fa09b55c547'

class PSProcessor():
    '''
    This class is a singleton, that is used to schedule powershell jobs.
    '''
    __instance = None

    def __new__(cls):
        if(cls.__instance is None):
            cls.__instance = super(PSProcessor, cls).__new__(cls)
        return cls.__instance
        
    def __init__(self) -> None:
        # self.process_queue = PSRestQueue()
        self.kill_queue = Queue()
        self.requests= Queue()
        self.process_alerts = Queue()
        self.process_count = PS_PROCESSORS
        Thread(target=self.start, name='PSProcessorScheduler').start()


    # async def request(self, command: Cmdlet) -> PSTicket:
    #     '''
    #     This method is used to request for a powershell job to be executed.
    #     '''
    #     #Create a ticket for the command and put it in the schedule
    #     ticket = PSTicket(command)
    #     self.requests.put(ticket.serialise())

    #     #Put the command on the process_queue
    #     try:
    #         await self.process_queue.put(
    #             json.dumps({'command': command.value, 'ticket': ticket.id})
    #         )
    #         return ticket
    #     except Exception as e:
    #         raise ProcessorException('Scheduler failed to schedule the command to a PSProcessor.')


    def execute(self, id: str, platform = 'pwsh'):
        try:
            result = subprocess.run(
                [f'{platform}', "-Command", f'Start-PSRestProcessor -ProcessId "{id}" -ResponsePath "{RESPONSE_DIR}" -SocketPath "{PSRESTQUEUE_PUT}""'],
                stdout=subprocess.DEVNULL)
        except Exception as e:
            #TODO: Log this error
            print(e)
    
    def start(self):
        '''
        This method is used to track the processes that are running. And what tickets they are processing.
        It kills processes that are taking too long to process a ticket. And issues a command to start a new one.
        '''
        processor = sqlite3.connect(':memory:')
        #Create the tables for the scheduler and processor process
        cursor = processor.cursor()
        #add a cascade to the schedule table so when a process is deleted, it's ticket is also deleted
        cursor.execute('CREATE TABLE PSProcessor (ticket TEXT PRIMARY KEY, pid TEXT, created REAL, expires REAL)')
        cursor.execute('CREATE TABLE PSProcess (pid TEXT PRIMARY KEY, last_seen REAL)')
        processor.commit()
        
        for x in range(self.process_count):
            id = uuid4().hex
            Process(name=(f'PSRestProcessor {id}'), target=self.execute, args=(id,)).start()

        while(True):
            print('Scheduler running')

if __name__ == '__main__':

    procesor = PSProcessor()
    while(True):
        sleep(1000)