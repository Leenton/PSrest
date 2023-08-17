#import webserver application and router
from falcon.asgi import App
import uvicorn
from threading import Thread
from LogHandler import LogHandler
from multiprocessing import Process
from queue import Queue
from subprocess import Popen, PIPE
from time import sleep
import os
import sqlite3

# #import endpoints
# from endpoints.Kill import Kill
# from endpoints.Running import Running
from endpoints.Help import Help
from endpoints.Run import Run
from endpoints.OAuth import OAuth
from endpoints.Home import Home
from endpoints.Resources import Resources
from endpoints.Processes import Processes
from endpoints.ProcessEvents import ProcessEvents
from entities.PSRestQueue import serve_queue
from processing.PSProcessor import start_processor
from Config import *


#import processing entities

if __name__ == '__main__':

    #check if the db exists if not create it
    if(not os.path.exists(DATABASE)):
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.executescript("""
        CREATE TABLE client (cid INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, client_secret TEXT, name TEXT, description TEXT, authentication TEXT);
        CREATE TABLE refresh_client_map (rid INTEGER PRIMARY KEY AUTOINCREMENT, refresh_token TEXT, expiry REAL, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);
        CREATE TABLE action_client_map (aid INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);
        """
        )

    # process = Popen(['python3', 'src/Queue.py'])
    #Handle the Python Powershell communication in a separate Process
    queue = Process(target=serve_queue, name='PSRestQueue')
    queue.start()
    sleep(5)

    kill = Queue()
    requests = Queue()
    alerts = Queue()
    stats = Queue()
    processes = Queue()

    processing = Thread(
        target=start_processor,
        name='PSProcessor',
        args=(kill, requests, alerts, stats, processes)
        )
    processing.start()

    #Start the webserver
    PSRest = App()

    PSRest.add_route('/', Home()) #Page to get all running processes
    PSRest.add_route('/oauth', OAuth()) #Page to get an access token
    PSRest.add_route('/run', Run(kill, requests, alerts, stats, processes)) #Page to run commands
    PSRest.add_route('/help', Help()) #Page to show help for PSRest
    PSRest.add_route('/help/{command}', Help()) #Page to show help for a specific command
    PSRest.add_route('/resources/{resource}', Resources()) #Page to return static files like images for help page
    PSRest.add_route('/processes', Processes())
    PSRest.add_route('/processes/{event_type}', ProcessEvents(stats, processes))

    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')
