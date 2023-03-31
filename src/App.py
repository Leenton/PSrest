#import webserver application and router
from falcon.asgi import App
import uvicorn
from threading import Thread
from LogHanlder import LogHanlder
from queue import Queue

#import endpoints
from endpoints.Kill import Kill
from endpoints.Running import Running
from endpoints.Help import Help
from endpoints.Run import Run
from endpoints.OAuth import OAuth
from endpoints.Resources import Resources
from Config import *

if __name__ == '__main__':
    # logger = LogHanlder()
    # logging = Thread(target=logger.start, args=())
    # logging.start()

    #Start the PSRest web server and listen on port 
    PSRest = App()
    # PSRest.add_route('/oauth', OAuth) #Page to get an access token
    PSRest.add_route('/run', Run()) #Page to run commands
    PSRest.add_route('/help', Help()) #Page to show help for PSRest
    PSRest.add_route('/help/{command}', Help()) #Page to show help for a specific command
    # PSRest.add_route('/kill/{ticket_id}', Kill()) #Page to kill a job
    # PSRest.add_route('/resources/{resource}', Resources()) #Page to return static files like images for help page
    # PSRest.add_route('/running', Running()) #Page to show all running jobs

    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')
