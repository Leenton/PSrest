#import webserver application and router
from falcon.asgi import App
import uvicorn
from threading import Thread
from multiprocessing import Process
from queue import Queue
from time import sleep
import os
import sqlite3

from endpoints.Help import Help
from endpoints.Run import Run
from endpoints.OAuth import OAuth
from endpoints.Home import Home
from endpoints.Resources import Resources
from endpoints.Processes import Processes
from endpoints.ProcessEvents import ProcessEvents
from psrlogging.Logger import ThreadSafeLogger
from entities.PSRestQueue import serve_queue
from processing.PSProcessor import start_processor
from psrlogging.PSRestLogger import start_logger
from configuration.Config import *


#import processing entities

if __name__ == '__main__':

    #Check if the db exists if not create it
    if(not os.path.exists(DATABASE)):
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.executescript("""
        CREATE TABLE client (cid INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, client_secret TEXT, name TEXT, description TEXT, authentication TEXT);
        CREATE TABLE refresh_client_map (rid INTEGER PRIMARY KEY AUTOINCREMENT, refresh_token TEXT, expiry REAL, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);
        CREATE TABLE action_client_map (aid INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);
        """
        )

    #Create queues for communication between threads and processes
    kill, requests, alerts, stats, processes, logs = Queue(), Queue(), Queue(), Queue(), Queue(), Queue()

    #Create threads and subproceses for processing and psrlogging and queueing
    processing = Thread(target=start_processor, name='PSProcessor', args=(kill, requests, alerts, stats, processes))
    psrlogging = Thread(target=start_logger, name='PSRestLogger',args=(logs,))
    psrest_queue = Process(target=serve_queue, name='PSRestQueue')
    
    #Start all the threads
    psrest_queue.start()
    psrlogging.start()
    sleep(5)
    processing.start()

    #Define the webserver application and add routes
    PSRest = App()
    logger = ThreadSafeLogger(logs)
    PSRest.add_route('/', Home(logger)) #Page to get all running processes
    PSRest.add_route('/oauth', OAuth(logger)) #Page to get an access token
    PSRest.add_route('/run', Run(kill, requests, alerts, stats, processes, logger)) #Page to run commands
    PSRest.add_route('/help', Help(logger)) #Page to show help for PSRest
    PSRest.add_route('/help/{command}', Help(logger)) #Page to show help for a specific command
    PSRest.add_route('/resources/{resource}', Resources(logger)) #Page to return static files like images for help page
    PSRest.add_route('/processes', Processes(logger))
    PSRest.add_route('/processes/{event_type}', ProcessEvents(stats, processes, logger))
    
    #Start the webserver
    logger.log('Starting PSRest')
    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')
