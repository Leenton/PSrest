# import webserver application and router
from falcon.asgi import App
import uvicorn
from multiprocessing import Process, Queue as ProcessQueue
from subprocess import Popen
from time import sleep
import os

from endpoints.Help import Help
from endpoints.Run import Run
from endpoints.OAuth import OAuth
from endpoints.Home import Home
from endpoints.Resources import Resources
from endpoints.Processes import Processes
from endpoints.Events import Events
from psrlogging.MetricRecorderLogger import MultiProcessSafeRecorderLogger
from entities.PSRestQueue import serve_queue
from processing.PSProcessor import start_processor, PSProcessor
from psrlogging.Logger import start_logger, LogMessage
from psrlogging.MetricRecorder import start_metrics
from entities.ResourceMonitor import start_resource_monitor
from configuration.Config import *

if __name__ == '__main__':
    #Check if the databases exists if not create them
    if(not os.path.exists(CREDENTIAL_DATABASE)):
        setup_credential_db()

    if(not os.path.exists(METRIC_DATABASE)):
        setup_metric_db()

    setup_processor_db()

    #Create queues for communication between threads and processes
    requests, alerts, stats, processes, logs = ProcessQueue(), ProcessQueue(), ProcessQueue(), ProcessQueue(), ProcessQueue()

    #Create threads and subproceses for processing and psrlogging and queueing
    processing = Process(target=start_processor, name='PSProcessor', args=(requests, alerts, stats, processes))
    psrlogging = Process(target=start_logger, name='PSRestLogger',args=(logs,))
    resource_monitoring = Process(target=start_resource_monitor, name='PSRestResourceMonitor')
    # psrest_queue = Process(target=serve_queue, name='PSRestQueue')
    metrics = Process(target=start_metrics, name='PSRestMetrics', args=(stats,))
    
    #Start all the threads
    # Popen("python3 ./Queue.py", shell=True)
    # psrest_queue.start()
    resource_monitoring.start()
    psrlogging.start()
    metrics.start()
    sleep(2)
    processing.start()

    #Define the webserver application and add routes
    PSRest = App()
    logger = MultiProcessSafeRecorderLogger(logs, stats)
    processor = PSProcessor(requests, alerts, stats, processes)
    PSRest.add_route('/', Home(logger)) #Page to get all running processes
    PSRest.add_route('/oauth', OAuth(logger)) #Page to get an access token
    PSRest.add_route('/run', Run(processor, logger)) #Page to run commands
    PSRest.add_route('/help', Help(logger)) #Page to show help for PSRest
    PSRest.add_route('/help/{command}', Help(logger)) #Page to show help for a specific command
    PSRest.add_route('/resources/{resource}', Resources(logger)) #Page to return static files like images for help page
    PSRest.add_route('/processes', Processes(logger))
    PSRest.add_route('/events/{event_type}', Events(processes, stats, logger))
    
    #Start the webserver
    logger.log(LogMessage("Starting PS Rest"))
    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')