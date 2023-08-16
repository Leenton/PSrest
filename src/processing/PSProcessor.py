from multiprocessing import Process, active_children
import subprocess
from uuid import uuid4
from entities.PSTicket import PSTicket
from entities.Cmdlet import Cmdlet 
from entities.PSRestQueue import PSRestQueue
import json 
from exceptions.PSRExceptions import ProcessorException
import sqlite3
from datetime import datetime
from Config import *
from threading import Thread
from queue import Queue
from processing.PSProcess import PSProcess
from time import sleep
from entities.PSRestQueue import PSRQueueException
from threading import Thread
from sqlite3.dbapi2 import Connection
from threading import Lock

class PSProcessor():
    def __init__(
            self,
            kill: Queue,
            requests: Queue,
            alerts: Queue,
            stats: Queue = Queue(),
            processes: Queue = Queue(),
        ) -> None:

        self.process_queue = PSRestQueue()
        self.kill = kill
        self.requests = requests
        self.alerts = alerts
        self.process_count = PS_PROCESSORS
        self.stats = stats
        self.processes = processes

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
        #Check the kill queuue for processes that we have been told to kill
        try:
            pid = self.kill.get(False)
            if(pid):
                #Kill the process and update the database
                for child in active_children():
                    if child.name == pid:
                        #TODO: Log this
                        #log how long the process was running for before it was killed
                        child.terminate()

                cursor = processor_db.cursor()
                print("DELETING PROCESS")
                cursor.execute(
                    'DELETE FROM PSProcess WHERE pid = ?',
                    [pid]
                )
                processor_db.commit()
        except Exception:
            #TODO: Log this
            pass

    def accept_requests(self, processor_db: Connection) -> None:
        #Check the requests queue and add them to the database
        try:
            ticket = self.requests.get(False)
            if(ticket):
                cursor = processor_db.cursor()
                cursor.execute(
                    'INSERT INTO PSProcessor (ticket, application, command, pid, processed, created, expires, modified) VALUES (?, ?, ?, ?, ?, ? , ?, ?)',
                    (ticket['id'], ticket['application_name'], ticket['command'], None, None, ticket['created'], ticket['expires'], datetime.timestamp(datetime.now()))
                )
        except Exception:
            #TODO: Log this
            pass

    def process_alerts(self, processor_db: Connection) -> None:
        #Check the alerts queue and match them to the tickets in the database
        try:
            process_alert:dict = self.alerts.get(False)
            if(process_alert.get('status', None)):
                #Delete the ticket from the database
                cursor = processor_db.cursor()
                cursor.execute('DELETE FROM PSProcessor WHERE ticket = ?', (process_alert['ticket'],))
                processor_db.commit()

                if(process_alert['status'] == FAILED):
                    #kill the process that was executing the command
                    self.kill.put(process_alert['pid'])
                
            elif(process_alert.get('pid', None)):
                cursor = processor_db.cursor()
                cursor.execute('UPDATE PSProcessor SET pid = ? WHERE ticket = ?',
                    (process_alert['pid'], process_alert['ticket'])
                )
                processor_db.commit()
                cursor = processor_db.cursor()
                cursor.execute('UPDATE PSProcess SET last_seen = ? WHERE pid = ?',
                    ((datetime.timestamp(datetime.now())), process_alert['pid'])
                )
                processor_db.commit()
        except Exception:
            pass

    def scale_up_processes(self, processor_db: Connection) -> None:
        #If there are tickets that have been waiting for too long, spin up a new process to process them
        try:
            cursor = processor_db.cursor()
            cursor.execute(
                'SELECT ticket FROM PSProcessor WHERE pid IS NULL AND created < ?',
                [datetime.timestamp(datetime.now()) - TOO_LONG]
            )
            tickets = cursor.fetchall()

            #if the ticket length is greater than 0, and we haven't reached the max number of processes
            if(len(tickets) > 0 and len(active_children()) < MAX_PROCESSES):
                #spin up a new process to process the requests
                psprocess = PSProcess()
                Thread(name=(f'PSProcess {psprocess.id}'), target=psprocess.execute).start()
        except Exception:
            pass
    
    def scale_down_processes(self, processor_db: Connection) -> None:
        pass

    def update_process_stats(self, processor_db: Connection) -> None:
        self.processes.get()
        cursor = processor_db.cursor()
        cursor.execute('SELECT * FROM PSProcessor')
        processes = cursor.fetchall()
        processes = map(
            lambda x: {
                'ticket': x[0],
                'pid': x[1],
                'application': x[2],
                'command': x[3],
                'created': x[4],
                'expires': x[5],
                'modified': x[6]
            },
            processes)
        self.processes.put(processes)

        self.stats.get()
        #get the number of process threads that are running
        self.stats.put({'shells': len(active_children())})
        


    def start(self):
        '''
        This method is used to track the processes that are running. And what tickets they are processing.
        It kills processes that are taking too long to process a ticket. And issues a command to start a new one.
        '''
        db = sqlite3.connect(':memory:')
        cursor = db.cursor()
        #add a cascade to the schedule table so when a process is deleted, it's ticket is also deleted
        cursor.execute('CREATE TABLE PSProcessor (ticket TEXT PRIMARY KEY, pid TEXT, application TEXT, command TEXT, created REAL, expires REAL, modified REAL)')
        cursor.execute('CREATE TABLE PSProcess (pid TEXT PRIMARY KEY, last_seen REAL) FOREIGN KEY(pid) REFERENCES PSProcessor(pid) ON DELETE CASCADE')
        db.commit()
        
        for x in range(self.process_count):
            psprocess = PSProcess()
            Thread(name=(f'PSProcess {psprocess.id}'), target=psprocess.execute).start()

        while(True):
            self.kill_processes(db)
            self.process_alerts(db)
            self.accept_requests(db)
            self.scale_up_processes(db)
            self.scale_down_processes(db)
            self.update_process_stats(db)

def start_processor(kill: Queue, requests: Queue, alerts: Queue, stats: Queue, processes: Queue):
    processor = PSProcessor(kill, requests, alerts, stats, processes)
    processes.put([])
    processor.start()