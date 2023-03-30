#import dependecies for reading the config file. 
from pathlib import Path
import configparser
from uuid import uuid4

CONFIG = configparser.ConfigParser()      
CONFIG.read_file(open((str(Path(__file__).parent.parent) + '/config'), 'r')) 
HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
PORT = CONFIG.get('Server', 'PORT')
CMDLET_TTL = CONFIG.get('TimeOut', 'CMDLET_TTL')
TICKET_TTL = CONFIG.get('TimeOut', 'TICKET_TTL')
PRIVATE_KEY = 'sdjhwdkjwqhdqajkwhdqjkwhdqjkwhdqwjkdhqwdqwd'
PUBLIC_KEY = 'sdjhwdkjwqhdqajkwhdqjkwhdqjkwhdqwjkdhqwdqwd'
PS_PROCESSORS =4
ARBITRARY_COMMANDS = CONFIG.get('PSExecution', 'ARBITRARY_COMMANDS')
CHANNEL = uuid4().hex
HELP = CONFIG.get('Help', 'HELP')
MODULES = CONFIG.get('ExposedModules', 'MODULES')
DISABLE_COMMANDS = CONFIG.get('DisabledCmdlets', 'CMDLETS')
ENABLE_COMMANDS = CONFIG.get('EnableCmdlets', 'CMDLETS')

#We should sanatise our constants so we know they are safe before the application just rolls with it.

