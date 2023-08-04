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
from Config import PS_PROCESSORS
from threading import Thread
from queue import Queue
from processing.PSProcess import PSProcess
from time import sleep
from entities.PSRestQueue import PSRQueueException
from threading import Thread

class PSProcessor():
    def __init__(self, kill: Queue, requests: Queue, alerts: Queue) -> None:
        self.process_queue = PSRestQueue()
        self.kill = kill
        self.requests = requests
        self.alerts = alerts
        self.process_count = PS_PROCESSORS

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
            psprocess = PSProcess()
            Thread(name=(f'PSProcess {psprocess.id}'), target=psprocess.execute).start()

        while(True):
            sleep(1)
        # while(True):
            #Check request queue for new requests
            # try:
            #     ticket = self.requests.get(False)
            #     cursor = processor.cursor()
            #     cursor.execute(
            #         'INSERT INTO PSProcessor (ticket, pid, processed, created, expires) VALUES (?, ?, ?, ?, ?)',
            #         (ticket['id'], None, None, ticket['created'], ticket['expires'])
            #     )
            # except Exception:
            #     pass
            
            # #Check to see which processes have been killed and update the database
            # try:
            #     pid = self.kill.get(False)
            #     cursor = processor.cursor()
            #     print("DELETING PROCESS")
            #     cursor.execute(
            #         'DELETE FROM PSProcess WHERE pid = ?',
            #         [pid]
            #     )
            #     processor.commit()
            # except Exception:
            #     pass

            # #Check the alerts queue for jobs picked up by processes
            # try:
            #     process_alert = self.alerts.get(False)
            #     print("UPDATING TICKET")
            #     cursor = processor.cursor()
            #     cursor.execute('UPDATE PSProcessor SET pid = ? WHERE ticket = ?',
            #         (process_alert['pid'], process_alert['ticket'])
            #     )
            #     processor.commit()
            #     cursor = processor.cursor()
            #     cursor.execute('UPDATE PSProcess SET last_seen = ? WHERE pid = ?',
            #         ((datetime.timestamp(datetime.now())), process_alert['pid'])
            #     )
            #     processor.commit()
            # except Exception:
            #     pass

            # sleep(0.001)

            # #Check the kill for processes that we have been told to kill
            # try:
            #     pid = self.kill.get(False)
            #     cursor = processor.cursor()
            #     cursor.execute('DELETE FROM PSProcess WHERE pid = ?', [pid])
            #     processor.commit()
            #     for child in active_children():
            #         if child.name == pid:
            #             #TODO: Log this
            #             #log how long the process was running for before it was killed
            #             child.terminate()

            # except Exception:
            #     pass
            
            # #If there are tickets that have been waiting for too long, spin up a new process to process them
            # try:
            #     cursor = processor.cursor()
            #     cursor.execute(
            #         'SELECT ticket FROM PSProcessor WHERE pid IS NULL AND created < ?',
            #         [datetime.timestamp(datetime.now()) - 0.25]
            #     )
            #     tickets = cursor.fetchall()
            #     if(len(tickets) > 0):
            #         #spin up a new process to process the ticket
            #         psprocess = PSProcess()
            #         Process(name=(f'PSRestProcessor {psprocess.id}'), target=psprocess.execute).start()
            # except Exception:
            #     pass

            # #Check for processes that are processing tickets that have expired
            # try:
            #     cursor = processor.cursor()
            #     cursor.execute(
            #         'SELECT pid FROM PSProcessor WHERE pid IS NOT NULL AND expires < ?',
            #         [int(datetime.timestamp(datetime.now()))]
            #     )
            #     processes = cursor.fetchall()
            #     if(len(processes) > 0):
            #         #kill the processor
            #         for process in processes:
            #             self.kill.put(process['pid'])
            #             cursor = processor.cursor()
            #             cursor.execute('DELETE FROM PSProcessor WHERE pid = ?', [process['pid']])
            #             processor.commit()
            # except Exception:
            #     pass

            # #Check the number of processes running, and start a new one if there are less than the number we want
            # running_psrestprocessors = 0
            # for child in active_children():
            #     if child.name.startswith('PSRestProcessor'):
            #         running_psrestprocessors += 1
        
            # if(running_psrestprocessors < self.process_count):
            #     psprocess = PSProcess()
            #     Process(name=(f'PSRestProcessor {psprocess.id}'), target=psprocess.execute).start()
            


def start_processor(kill = Queue(), requests = Queue(), alerts = Queue()):
    processor = PSProcessor(kill, requests, alerts)
    processor.start()