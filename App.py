# import webserver application and router
from falcon.asgi import App
import uvicorn
from multiprocessing import Process, Queue as ProcessQueue
from time import sleep
import os

from configuration import (
    CREDENTIAL_DATABASE,
    PORT,
    setup_credential_db
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

if __name__ == '__main__':
    #Check if the databases exists if not create them
    if(not os.path.exists(CREDENTIAL_DATABASE)):
        setup_credential_db()

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
    PSRest.add_route('/', Home(logger)) #Page to get all running processes
    PSRest.add_route('/oauth', OAuth(logger)) #Page to get an access token
    PSRest.add_route('/run', Run(logger)) #Page to run commands
    PSRest.add_route('/docs', Docs(logger)) #Page to show documentation for PSRest
    PSRest.add_route('/help/{command}', Help(logger)) #Page to show help for a specific command
    PSRest.add_route('/resources/{resource}', Resources(logger)) #Page to return static files like images for help page
    
    #Start the webserver
    logger.log(Message("Starting PS Rest"))
    # TODO: 
    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')