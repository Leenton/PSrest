from multiprocessing import Process, active_children, Queue
import subprocess
import asyncio
from uuid import uuid4
import json 
from datetime import datetime
from threading import Thread
from time import sleep
from threading import Thread
from sqlite3.dbapi2 import Connection
from sqlite3 import connect

#Internal imports
from configuration.Config import *
from exceptions.PSRExceptions import ProcessorException
from processing.PSProcess import PSProcess
from entities.PSRestQueue import PSRestQueue, PSRQueueException
from entities.PSRestKillQueue import PSRestKillQueue
from entities.PSTicket import PSTicket
from entities.Cmdlet import Cmdlet 

class PSProcessor():
    def __init__(
            self,
            requests: Queue,
            alerts: Queue,
            stats: Queue = Queue(),
            processes: Queue = Queue(),
        ) -> None:

        self.process_queue = PSRestQueue()
        self.kill_queue = PSRestKillQueue()
        self.requests = requests
        self.alerts = alerts
        self.process_count = PS_PROCESSORS
        self.stats = stats
        self.processes = processes
        self.accepted_request_this_tick = False
        self.sleep_time = 1 / PROCESSOR_TICK_RATE
        self.processors = {}
        self.this_tick = datetime.timestamp(datetime.now())
        self.next_spawn = self.this_tick + PROCESSOR_SPIN_UP_PERIOD

    async def request(self, command: Cmdlet) -> PSTicket: 
        '''
        This method is used to request for a powershell job to be executed.
        '''
        #Create a ticket for the command and put it in the schedule
        ticket = PSTicket(command)
        self.requests.put(ticket.serialise())

        #Put the command on the process_queue
        try:
            await self.process_queue.put(
                json.dumps({'Command': command.value, 'Ticket': ticket.id, 'Depth': command.depth})
            )
            return ticket
        except PSRQueueException as e:
            raise ProcessorException('Scheduler failed to schedule the command to a PSProcessor.')
    
    async def send_result(self, alert: dict) -> None:
        self.alerts.put(alert)

    def kill_processes(self, processor_db: Connection) -> None:
        #Check the kill queue for processes that we have been told to kill
        try:
            pid = self.kill_queue.get('1')
            if(pid):
                #Kill the process and update the database
                for child in active_children():
                    if child.name == pid:
                        #TODO: Log this
                        #log how long the process was running for before it was killed
                        child.terminate()

                cursor = processor_db.cursor()
                print("DELETING PROCESS")
                cursor.execute("DELETE FROM PSProcess WHERE pid = ?", [pid])
                processor_db.commit()
        except Exception:
            #TODO: Log this
            return

    def accept_requests(self, processor_db: Connection) -> None:
        #Check the requests queue and add them to the database
        try:
            ticket = self.requests.get(False)
            if(ticket):
                cursor = processor_db.cursor()
                cursor.execute(
                    "INSERT INTO PSProcessor (ticket, application, command, pid, created, expires, modified) VALUES (?, ?, ?, ?, ?, ? , ?)",
                    (ticket['id'], ticket['application_name'], ticket['command'], None, ticket['created'], ticket['expires'], self.this_tick)
                )
                processor_db.commit()
                self.accepted_request_this_tick = True

        except Exception:
            return

    async def process_alerts(self, processor_db: Connection) -> None:
        #Check the alerts queue and alert sources and match them to the tickets in the database

        process_alert:dict = json.loads(self.process_queue.get())
        if(process_alert.get('pid', None)):
            cursor = processor_db.cursor()
            cursor.execute(
                "UPDATE PSProcessor SET pid = ? WHERE ticket = ?",
                (process_alert['pid'], process_alert['ticket'])
            )
            processor_db.commit()
            cursor = processor_db.cursor()
            cursor.execute(
                "UPDATE PSProcess SET last_seen = ? WHERE pid = ?",
                (self.this_tick, process_alert['pid'])
            )
            processor_db.commit()
                
        try:
            process_alert:dict = self.alerts.get(False)
            if(process_alert.get('status', None)):
                #Delete the ticket from the database
                cursor = processor_db.cursor()
                cursor.execute(
                    "DELETE FROM PSProcessor WHERE ticket = ?",
                    (process_alert['ticket']['id'],))
                processor_db.commit()

                if(process_alert['status'] == FAILED):
                    #kill the process that was executing the command
                    cursor = processor_db.cursor()
                    cursor.execute(
                        "SELECT pid FROM PSProcessor WHERE ticket = ?",
                        (process_alert['ticket']['id'],)
                    )
                    pid = cursor.fetchone()[0]
                    self.kill_queue.kill(pid)

        except Exception:
            return

    def scale_up_processes(self, processor_db: Connection) -> None:
        #If there are tickets that have been waiting for too long, spin up a new process to process them
        try:
            cursor = processor_db.cursor()
            cursor.execute("""--sql
                SELECT ticket, created, pid
                FROM PSProcessor
                WHERE pid IS NULL AND created < ?
                ORDER BY created ASC
                """,
                [self.this_tick - TOO_LONG]
            )
            tickets = cursor.fetchall()

            #if the ticket length is greater than 0, and we haven't reached the max number of processes
            if(
                len(tickets) > 0
                and len(self.processors) < MAX_PROCESSES
                and self.this_tick  > self.next_spawn
                and tickets[0][1] < self.this_tick - PROCESSOR_SPIN_UP_PERIOD
            ):
                #spin up a new process to process the requests
                self.spawn_psprocess(processor_db)
                self.next_spawn = self.this_tick + PROCESSOR_SPIN_UP_PERIOD
        except Exception:
            return
    
    def scale_down_processes(self, processor_db: Connection) -> None:
        #if there is a process that hasn't been seen for a while and it has no tickets assigned to it, kill it
        try:
            cursor = processor_db.cursor()
            cursor.execute("""
                SELECT pid
                FROM PSProcess
                LEFT JOIN PSProcessor ON PSProcess.pid = PSProcessor.pid
                WHERE PSProcess.last_seen < ?
                AND PSProcessor.ticket IS NULL
                """,
                (self.this_tick - int(DEFAULT_TTL)/2,)
            )
            pids = cursor.fetchall()

            #if the ticket length is greater than 0, and we haven't reached the max number of processes
            for pid in pids:
                self.kill_queue.kill(pid[0])

        except Exception:
            return
    
    def spawn_psprocess(self, processor_db: Connection) -> None:
        psprocess = PSProcess()
        process = Thread(name=(f'PSProcess {psprocess.id}'), target=psprocess.execute)

        cursor = processor_db.cursor()
        cursor.execute(
            "INSERT INTO PSProcess (pid, last_seen) VALUES (?, ?)",
            (psprocess.id, self.this_tick))
        processor_db.commit()
        process.start()
        self.processors[psprocess.id] = process


    def sleep(self) -> None:
        #Calulate the sleep time based on how busy the processor is and how many requests are coming in
        if(self.accepted_request_this_tick):
            self.accepted_request_this_tick = False
            self.sleep_time = 1 / PROCESSOR_TICK_RATE
        elif(self.sleep_time > 0.25):
            self.sleep_time = 0.25
        else:
            self.sleep_time = self.sleep_time * 2
        
        sleep(self.sleep_time)

    def start(self):
        '''
        This method is used to track the processes that are running. And what
        tickets they are processing. It kills processes that are taking too
        long to process a ticket. And issues a command to start a new one.
        '''
        db = connect(PROCESSOR_DATABASE)
        
        for x in range(self.process_count):
            self.spawn_psprocess(db)

        while(True):
            self.kill_processes(db)
            self.accept_requests(db)
            asyncio.run(self.process_alerts(db))
            self.scale_up_processes(db)
            # self.scale_down_processes(db)

            self.sleep()
            self.this_tick = datetime.timestamp(datetime.now())
            
def start_processor(requests: Queue, alerts: Queue, stats: Queue, processes: Queue):
    processor = PSProcessor(requests, alerts, stats, processes)
    processes.put([])
    processor.start()