#import webserver application and router
from falcon.asgi import App
import uvicorn
from threading import Thread
from LogHanlder import LogHanlder
from multiprocessing import Process
from queue import Queue
from subprocess import Popen, PIPE

# #import endpoints
# from endpoints.Kill import Kill
# from endpoints.Running import Running
from endpoints.Help import Help
from endpoints.Run import Run
from endpoints.OAuth import OAuth
from endpoints.Resources import Resources
from entities.PSRestQueue import serve_queue
from processing.PSProcessor import start_processor
from Config import *


#import processing entities

if __name__ == '__main__':

    # process = Popen(['python3', 'src/Queue.py'])
    #Handle the Python Powershell communication in a separate Process
    queue = Process(target=serve_queue, name='PSRestQueue')
    queue.start()

    kill = Queue()
    requests = Queue()
    alerts = Queue()
    processing = Thread(target=start_processor, name='PSProcessor', args=(kill, requests, alerts))
    processing.start()
    # processing = Process(target=start_processor, name='PSProcessor', args=(kill, requests, alerts))
    # processing.start()

    #Start the PSRest web server and listen on port 
    PSRest = App()
    
    PSRest.add_route('/oauth', OAuth()) #Page to get an access token
    
    # PSRest.add_route('/run', Run(kill, requests, alerts)) #Page to run commands
    # PSRest.add_route('/help', Help()) #Page to show help for PSRest
    # PSRest.add_route('/help/{command}', Help()) #Page to show help for a specific command
    
    # PSRest.add_route('/kill/{ticket_id}', Kill()) #Page to kill a job
    # PSRest.add_route('/resources/{resource}', Resources()) #Page to return static files like images for help page
    # PSRest.add_route('/running', Running()) #Page to show all running jobs

    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')
