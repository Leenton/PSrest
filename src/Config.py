#import dependecies for reading the config file. 
from pathlib import Path
import configparser
from uuid import uuid4
from os import path

CONFIG = configparser.ConfigParser()      
CONFIG.read_file(open((str(Path(__file__).parent.parent) + '/config'), 'r')) 
HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
PORT = CONFIG.get('Server', 'PORT')

#Constants for the ticketing system
DEFAULT_TTL = CONFIG.get('TimeOut', 'DEFAULT_TTL')
MAX_TTL = CONFIG.get('TimeOut', 'MAX_TTL')

#Constants for the encryption
SECRET_KEY = ''
PRIVATE_KEY = ''
PUBLIC_KEY = ''

#Constants for the powershell execution
PS_PROCESSORS =4
ARBITRARY_COMMANDS = True if ((CONFIG.get('PSExecution', 'ARBITRARY_COMMANDS')).lower() == 'true') else False
HELP = CONFIG.get('Help', 'HELP')
MODULES = CONFIG.get('ExposedModules', 'MODULES')
DISABLE_COMMANDS = CONFIG.get('DisableCmdlets', 'CMDLETS')
ENABLE_COMMANDS = CONFIG.get('EnableCmdlets', 'CMDLETS')

#Constants for storage and socket communication

TMP_DIR = path.abspath("./tmp")
RESPONSE_DIR = TMP_DIR + '/' + 'resp'
PSRESTQUEUE_PUT = TMP_DIR + '/' + '5a682fbbe1bc487793d55fa09b55c547'
PSRESTQUEUE_GET = TMP_DIR + '/' + '95b51250d7ef4fcdaea1cf51886b8ba5'
PSRESTQUEUE_SRV = TMP_DIR + '/' +' fcf29f8069d646e8bdc75af3eb7f02e4'

#TODO: Sanitise the contents we get from the config file to prevent code injection.

