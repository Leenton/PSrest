#import dependecies for reading the config file. 
from pathlib import Path
import configparser
from uuid import uuid4

CONFIG = configparser.ConfigParser()      
CONFIG.read_file(open((str(Path(__file__).parent.parent) + '/config'), 'r')) 
HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
PORT = CONFIG.get('Server', 'PORT')

#Constants for the ticketing system
DEFAULT_TTL = CONFIG.get('TimeOut', 'DEFAULT_TTL')

#Constants for the encryption
SECRET_KEY = 'sdjhwdkjwqhdqajkwhdqjkwhdqjkwhdqwjkdhqwdqwd'
PRIVATE_KEY = 'sdjhwdkjwqhdqajkwhdqjkwhdqjkwhdqwjkdhqwdqwd'
PUBLIC_KEY = 'sdjhwdkjwqhdqajkwhdqjkwhdqjkwhdqwjkdhqwdqwd'

#Constants for the powershell execution
PS_PROCESSORS =4
ARBITRARY_COMMANDS = CONFIG.get('PSExecution', 'ARBITRARY_COMMANDS')
HELP = CONFIG.get('Help', 'HELP')
MODULES = CONFIG.get('ExposedModules', 'MODULES')
DISABLE_COMMANDS = CONFIG.get('DisableCmdlets', 'CMDLETS')
ENABLE_COMMANDS = CONFIG.get('EnableCmdlets', 'CMDLETS')

#Constants for storage and socket communication
TMP_DIR = "./tmp"
RESPONSE_DIR = TMP_DIR + '/' + 'resp'
PSRESTQUEUE_PUT = TMP_DIR + '/' + uuid4().hex
PSRESTQUEUE_GET = TMP_DIR + '/' + uuid4().hex
PSRESTQUEUE_SERVE = TMP_DIR + '/' + uuid4().hex

#TODO: Sanitise the contents we get from the config file to prevent code injection.

