# import webserver application and router
from falcon.asgi import App
import uvicorn
from multiprocessing import Process, Queue as ProcessQueue
from time import sleep
import os

from configuration import (
    METRIC_DATABASE,
    CREDENTIAL_DATABASE,
    PORT,
    setup_credential_db,
    setup_metric_db
)
from endpoints import(
    Help,
    Run,
    OAuth,
    Home,
    Resources,
    Processes,
    Events
)
from processing import start_processor, start_resource_monitor
from log import start_logging, LogClient, Message

if __name__ == '__main__':
    #Check if the databases exists if not create them
    if(not os.path.exists(CREDENTIAL_DATABASE)):
        setup_credential_db()

    if(not os.path.exists(METRIC_DATABASE)):
        setup_metric_db()

    #Create queues for communication between threads and processes
    metrics, messages = ProcessQueue(), ProcessQueue()

    #Create threads and subproceses for processing and logging and metrics handling
    processing = Process(target=start_processor, name='Processor')
    logging = Process(target=start_logging, name='Log',args=(messages, metrics))
    resource_monitoring = Process(target=start_resource_monitor, name='Resource Monitor')

    processing.start()
    sleep(3)
    resource_monitoring.start()
    logging.start()
    sleep(2)

    #Define the webserver application and add routes
    PSRest = App()
    logger: LogClient = LogClient(messages, metrics)
    PSRest.add_route('/', Home(logger)) #Page to get all running processes
    PSRest.add_route('/oauth', OAuth(logger)) #Page to get an access token
    PSRest.add_route('/run', Run(logger)) #Page to run commands
    PSRest.add_route('/help', Help(logger)) #Page to show help for PSRest
    PSRest.add_route('/help/{command}', Help(logger)) #Page to show help for a specific command
    PSRest.add_route('/resources/{resource}', Resources(logger)) #Page to return static files like images for help page
    PSRest.add_route('/processes', Processes(logger))
    PSRest.add_route('/events', Events(logger))
    
    #Start the webserver
    logger.log(Message("Starting PS Rest"))
    # TODO: 
    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')