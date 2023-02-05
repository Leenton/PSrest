#import dependecies for reading the config file. 
from pathlib import Path
import configparser


CONFIG = configparser.ConfigParser()      
CONFIG.read_file(open((str(Path(__file__).parent.parent) + '/config'), 'r')) 
HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
PORT = CONFIG.get('Server', 'PORT')
CMDLTTTL = CONFIG.get('TimeOut', 'CMDLTTTL')
TICKETTTL = CONFIG.get('TimeOut', 'TICKETTTL')