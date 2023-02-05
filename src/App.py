#import dependecies for reading the config file. 
from pathlib import Path
import configparser

#import webserver application and router
from falcon.asgi import App
import uvicorn

#import endpoints
from endpoints.Help import Help
from endpoints.Run import Run

if __name__ == "__main__":
    
    #Load configuration details form the config file in the config file. 
    CONFIG = configparser.ConfigParser()      
    CONFIG.read_file(open((str(Path(__file__).parent.parent) + "/config"), "r")) 
    HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
    PORT = CONFIG.get('Server', 'PORT')

    #Start the PSRest web server and listen on port 
    PSRest = App()
    PSRest.add_route('/run', Run())
    PSRest.add_route('/help', Help())
    PSRest.add_route('/help/{command}', Help())
    PSRest.add_route('/kill', Help())
    PSRest.add_route('/running', Help())

    uvicorn.run(PSRest, host="0.0.0.0", port=PORT, log_level='info')
