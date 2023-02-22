#import dependecies for reading the config file. 
from pathlib import Path
import configparser


CONFIG = configparser.ConfigParser()      
CONFIG.read_file(open((str(Path(__file__).parent.parent) + '/config'), 'r')) 
HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
PORT = CONFIG.get('Server', 'PORT')
CMDLT_TTL = CONFIG.get('TimeOut', 'CMDLT_TTL')
TICKET_TTL = CONFIG.get('TimeOut', 'TICKET_TTL')
PRIVATE_KEY = 'sdjhwdkjwqhdqajkwhdqjkwhdqjkwhdqwjkdhqwdqwd'
PUBLIC_KEY = 'sdjhwdkjwqhdqajkwhdqjkwhdqjkwhdqwjkdhqwdqwd'
PS_PROCESSORS = 16