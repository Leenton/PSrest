from entities.Cmdlet import Cmdlet
from entities.PSTicket import PSTicket
from entities.PSRestQueue import PSRestQueue
import asyncio
import json
import sqlite3
from Config import *
from datetime import datetime
from processing.PSProcessor import PSProcessor
from threading import Thread
from multiprocessing import Queue
from time import sleep
class PSScheduler():
    '''
    This class is a singleton, that is used to schedule powershell jobs.
    '''
    __instance = None

    def __new__(cls):
        if(cls.__instance is None):
            cls.__instance = super(PSScheduler, cls).__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        self.schedule = None
        self.PSProcessQueue = PSRestQueue()
        self.PSProcessor = PSProcessor(Queue(), Queue(), 'HALLO')
        self.overflow_queue = Queue()
        self.kill_queue = Queue()
        self.request_queue = Queue()

        Thread(target=self.PSProcessor.start, args=(
            PS_PROCESSORS,
            self.overflow_queue,
            self.kill_queue,
        )).start()
        sleep(10)
        Thread(target=self.schedule_processor).start()
    
    def request(self, command: Cmdlet) -> PSTicket|None:
        '''
        This method is used to request a powershell job to be executed.
        '''
        #Create a ticket for the command and put it in the schedule
        ticket = PSTicket()
        self.request_queue.put(ticket.serialise())

        #Put the command on the PSProcessQueue
        try:
            asyncio.run(self.PSProcessQueue.put(
                f'{CHANNEL}',
                json.dumps({'command': command.value(), 'ticket': ticket.id})
            ))
            return ticket
        except Exception as e:
            #TODO: Log this error
            print(e)
            return None

    def schedule_processor(self):
        self.schedule = sqlite3.connect(':memory:')

        #Create the tables for the scheduler and processor procsses
        cursor = self.schedule.cursor()
        cursor.execute('CREATE TABLE PSSchedule (ticket TEXT PRIMARY KEY, pid TEXT, processed INTEGER, created INTEGER, expires INTEGER)')
        cursor.execute('CREATE TABLE PSProcess (pid TEXT PRIMARY KEY, last_seen INTEGER)')
        self.schedule.commit()

        while(True):
            #insert any new tickets into the schedule from the RestQueue
            try:
                ticket = self.request_queue.get(False)
                cursor = self.schedule.cursor()
                cursor.execute(
                    'INSERT INTO PSSchedule (ticket, pid, processed, created, expires) VALUES (?, ?, ?, ?, ?)',
                    (ticket.id, None, None, ticket.created, ticket.expires)
                )
            except Exception:
                pass

            #remove any expired tickets
            cursor = self.schedule.cursor()
            cursor.execute(
                'DELETE FROM PSSchedule WHERE expires < ?',
                [int(datetime.timestamp(datetime.now()))]
            )
            self.schedule.commit()

            #if there are queued requests that have not been processed within the last 5 seconds, start a new processor
            cursor = self.schedule.cursor()
            cursor.execute(
                'SELECT * FROM PSSchedule WHERE processed IS NULL AND pid IS NULL AND created < ?',
                [int(datetime.timestamp(datetime.now()))]
            )
            if(len(cursor.fetchall()) > 0):
                #start a new processor
                self.overflow_queue.put(True)

            #if there are processors that have been running but have not been seen in the last 60 seconds, kill them.
            cursor = self.schedule.cursor()
            cursor.execute(
                'SELECT pid FROM PSProcess WHERE last_seen > ? AND pid NOT IN (SELECT pid FROM PSSchedule WHERE pid IS NOT NULL)',
                [int(datetime.timestamp(datetime.now()) - 60)]
            )
            processes = cursor.fetchall()
            if(len(processes) > 0):
                #kill the processor
                for process in processes:
                    self.kill_queue.put(process)

            #if there are processors that have been running longer than their tickets expirey, kill them unless the ticet expirey is null
            cursor = self.schedule.cursor()
            cursor.execute(
                'SELECT pid FROM PSSchedule WHERE pid IS NOT NULL AND expires IS NOT NULL AND expires < ?',
                [int(datetime.timestamp(datetime.now()))]
            )
            processes = cursor.fetchall()
            if(len(processes) > 0):
                #kill the processor
                for process in processes:
                    self.kill_queue.put(process)
