from pathlib import Path
import json, configparser, ssl

hello = {
    "id": "04", 
    "name": "sunil", 
    "department": "HR"
}


if __name__ == "__main__":
    
    #Load configuration details form the config file in the config file. 

    CONFIG = configparser.ConfigParser()      
    CONFIG.read_file(open((str(Path(__file__).parent.parent) + "/config"), "r")) 
    HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
    PORT = CONFIG.get('Server', 'PORT')

    
    
    print("Server started http://%s:%s" % (HOSTNAME, PORT))

    print("Server stopped.")