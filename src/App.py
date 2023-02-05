

#import webserver application and router
from falcon.asgi import App
import uvicorn
from threading import Thread
from LogHanlder import LogHanlder

#import endpoints
from endpoints.Help import Help
from endpoints.Run import Run
from endpoints.OAuth import OAuth
from Config import *

if __name__ == '__main__':
    logging = Thread(target=LogHanlder.start, args=[])
    logging.start()
    
    #Start the PSRest web server and listen on port 
    PSRest = App()
    PSRest.add_route('/oauth', OAuth)
    PSRest.add_route('/run/{command}', Run())
    PSRest.add_route('/help', Help())
    PSRest.add_route('/help/{command}', Help())
    PSRest.add_route('/kill', Help())
    PSRest.add_route('/running', Help())



    uvicorn.run(PSRest, host='0.0.0.0', port=PORT, log_level='info')
