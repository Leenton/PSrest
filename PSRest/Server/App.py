#!/usr/bin/python

# import webserver application and router
from falcon.asgi import App
import uvicorn
from multiprocessing import Process, Queue as ProcessQueue
from time import sleep
import os
from entities import CmdletInfoLibrary
import sys
from configuration import (
    CERTIFICATE,
    KEY_FILE,
    KEYFILE_PASSWORD,
    CIPHERS,
    PORT,
    LOG_LEVEL,
    setup_credential_database
)
from endpoints import(
    Help,
    Run,
    OAuth,
    Home,
    Resources,
    Docs
)
from processing import start_processor
from log import start_logging, LogClient, Message

#Get optional arguments from command line that override the config values.
port = None
log_level = None

for arg in sys.argv:
    if(arg.startswith('--port=')):
        port = int(arg.split('=', 2)[1])
    elif(arg.startswith('--loglevel=')):
        log_level = arg.split('=', 2)[1]
    elif(arg.startswith('--help')):
        print('''App.py [OPTION]...
Run the PSRest webserver.

Optional arguments:
--port=PORT        The port to run the webserver on. Overrides the config value.
--loglevel=LEVEL   The log level to use. Overrides the config value.
--help             Show this help message and exit.''')
        exit(0)

if __name__ == '__main__':
    setup_credential_database()

    #Create queues for communication between threads and processes
    messages = ProcessQueue()

    #Create threads and subproceses for processing and logging handling
    processing = Process(target=start_processor, name='Processor')
    logging = Process(target=start_logging, name='Log',args=(messages,))

    processing.start()
    sleep(3)
    logging.start()
    sleep(2)

    #Define the webserver application and add routes
    PSRest = App()
    logger: LogClient = LogClient(messages)
    cmdlet_library = CmdletInfoLibrary()
    PSRest.add_route('/', Home(logger, cmdlet_library)) #Page to get all running processes
    PSRest.add_route('/oauth', OAuth(logger)) #Page to get an access token
    PSRest.add_route('/run', Run(logger, cmdlet_library)) #Page to run commands
    PSRest.add_route('/docs', Docs(logger)) #Page to show documentation for PSRest
    PSRest.add_route('/docs/{page}', Docs(logger)) #Page to show help for all commands
    PSRest.add_route('/help/{command}', Help(logger)) #Page to show help for a specific command
    PSRest.add_route('/resources/{resource}', Resources(logger)) #Page to return static files like images for help page

    logger.log(Message(f"Starting PS Rest"))
    try:
        uvicorn.run(
            PSRest,
            host='0.0.0.0',
            port=PORT if port == 0 or port == None else port,
            log_level=LOG_LEVEL if log_level == None else log_level,
            ssl_keyfile=KEY_FILE,
            ssl_certfile=CERTIFICATE,
            ssl_keyfile_password=KEYFILE_PASSWORD,
            ssl_ciphers=CIPHERS
        )
    except KeyboardInterrupt:
        logger.log(Message(f"Stopping PS Rest"))
        processing.terminate()
        logging.terminate()
