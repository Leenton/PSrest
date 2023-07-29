from multiprocessing import Process, active_children, Queue
import subprocess
from uuid import uuid4
from entities.PSTicket import PSTicket
from entities.Cmdlet import Cmdlet 
from entities.PSRestQueue import PSRestQueue
import json 
from exceptions.PSRExceptions import ProcessorException
import sqlite3
from datetime import datetime
from Config import PS_PROCESSORS

class PSProcessor():
    '''
    This class is a singleton, that is used to schedule powershell jobs.
    '''
    __instance = None

    def __new__(cls):
        if(cls.__instance is None):
            cls.__instance = super(PSProcessor, cls).__new__(cls)
        return cls.__instance
        
    def __init__(self, kill_queue: Queue, request_overflow_queue: Queue) -> None:
        self.PSProcessQueue = PSRestQueue()
        self.kill_queue = kill_queue
        self.request_overflow_queue = request_overflow_queue
        self.requests= Queue()
        self.process_alerts = Queue()
        self.process_count = PS_PROCESSORS

    async def request(self, command: Cmdlet) -> PSTicket:
        '''
        This method is used to request for a powershell job to be executed.
        '''
        #Create a ticket for the command and put it in the schedule
        ticket = PSTicket(command)
        self.requests.put(ticket.serialise())

        #Put the command on the PSProcessQueue
        try:
            await self.PSProcessQueue.put(
                json.dumps({'command': command.value, 'ticket': ticket.id})
            )
            return ticket
        except Exception as e:
            raise ProcessorException('Scheduler failed to schedule the command to a PSProcessor.')


    def execute(self, id: str, platform = 'pwsh'):
        try:
            result = subprocess.run(
                [f'{platform}', "-Command", f'Start-PSProcessor -ProcessID {id}'],
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
            #Check request queue for new requests
            try:
                ticket = self.requests.get(False)
                cursor = processor.cursor()
                cursor.execute(
                    'INSERT INTO PSProcessor (ticket, pid, processed, created, expires) VALUES (?, ?, ?, ?, ?)',
                    (ticket['id'], None, None, ticket['created'], ticket['expires'])
                )
            except Exception:
                pass
            
            #Check to see which processes have been killed and update the database
            try:
                pid = self.kill_queue.get(False)
                cursor = processor.cursor()
                cursor.execute(
                    'DELETE FROM PSProcess WHERE pid = ?',
                    [pid]
                )
                processor.commit()
            except Exception:
                pass

            #Check the process_alerts queue for jobs picked up by processes
            try:
                process_alert = self.process_alerts.get(False)
                cursor = processor.cursor()
                cursor.execute('UPDATE PSProcessor SET pid = ? WHERE ticket = ?',
                    (process_alert['pid'], process_alert['ticket'])
                )
                processor.commit()
                cursor = processor.cursor()
                cursor.execute('UPDATE PSProcess SET last_seen = ? WHERE pid = ?',
                    ((datetime.timestamp(datetime.now())), process_alert['pid'])
                )
                processor.commit()
            except Exception:
                pass

            #Check the kill_queue for processes that we have been told to kill
            try:
                pid = self.kill_queue.get(False)
                cursor = processor.cursor()
                cursor.execute('DELETE FROM PSProcess WHERE pid = ?', [pid])
                processor.commit()
                for child in active_children():
                    if child.name == pid:
                        #TODO: Log this
                        #log how long the process was running for before it was killed
                        child.terminate()

            except Exception:
                pass
            
            #If there are tickets that have been waiting for too long, spin up a new process to process them
            try:
                cursor = processor.cursor()
                cursor.execute(
                    'SELECT ticket FROM PSProcessor WHERE pid IS NULL AND created < ?',
                    [datetime.timestamp(datetime.now()) - 0.25]
                )
                tickets = cursor.fetchall()
                if(len(tickets) > 0):
                    #spin up a new process to process the ticket
                    id = uuid4().hex
                    Process(name=(f'PSRestProcessor {id}'), target=self.execute, args=(id,)).start()
            except Exception:
                pass

            #Check for processes that are processing tickets that have expired
            try:
                cursor = processor.cursor()
                cursor.execute(
                    'SELECT pid FROM PSProcessor WHERE pid IS NOT NULL AND expires < ?',
                    [int(datetime.timestamp(datetime.now()))]
                )
                processes = cursor.fetchall()
                if(len(processes) > 0):
                    #kill the processor
                    for process in processes:
                        self.kill_queue.put(process['pid'])
                        cursor = processor.cursor()
                        cursor.execute('DELETE FROM PSProcessor WHERE pid = ?', [process['pid']])
                        processor.commit()
            except Exception:
                pass

            #Check the number of processes running, and start a new one if there are less than the number we want
            running_psrestprocessors = 0
            for child in active_children():
                if child.name.startswith('PSRestProcessor'):
                    running_psrestprocessors += 1
        
            if(running_psrestprocessors < self.process_count):
                id = uuid4().hex
                Process(name=(f'PSRestProcessor {id}'), target=self.execute, args=(id,)).start()