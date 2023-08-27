#import dependecies for reading the config file. 
from pathlib import Path
import configparser
from uuid import uuid4
from os import path
from secrets import token_bytes
import platform
import sqlite3


CREDENTIAL_DATABASE = str(Path(__file__).parent.parent.parent) + '/data.db' #OAuth2 credential database
METRIC_DATABASE = str(Path(__file__).parent.parent.parent) + '/metrics.db' #Metric database
CONFIG = configparser.ConfigParser()      
CONFIG.read_file(open((str(Path(__file__).parent.parent.parent) + '/config'), 'r')) 
HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
PORT = int(CONFIG.get('Server', 'PORT'))

#Constants for the ticketing system
DEFAULT_TTL = CONFIG.get('TimeOut', 'DEFAULT_TTL')
MAX_TTL = int(CONFIG.get('TimeOut', 'MAX_TTL'))
ACCESS_TOKEN_TTL = 3600
REFRESH_TOKEN_TTL = 86400 * 14
#Constants for how we serve responses
DEFAULT_DEPTH = CONFIG.get('Response', 'DEFAULT_DEPTH')
MAX_DEPTH = 100
TOO_LONG = 0.25

#Constants for the encryption
SECRET_KEY = '2ed154d0c89362da0e2fc49257c5fb27c01cdfbc85238ea334e84dbc8eccfee3812b41add4149999b2277780b0edbdda4905f46f607fd3ffd8d3601113c1e7ae'
PRIVATE_KEY = ''
PUBLIC_KEY = ''

#Constants for the powershell execution
PS_PROCESSORS =4
MAX_PROCESSES = 33
ARBITRARY_COMMANDS = True if ((CONFIG.get('PSExecution', 'ARBITRARY_COMMANDS')).lower() == 'true') else False
HELP = CONFIG.get('Help', 'HELP')
MODULES = CONFIG.get('ExposedModules', 'MODULES')
DISABLE_COMMANDS = CONFIG.get('DisableCmdlets', 'CMDLETS')
ENABLE_COMMANDS = CONFIG.get('EnableCmdlets', 'CMDLETS')
COMPETED = 'completed'
FAILED = 'failed'

#Constants for storage and socket communication
TMP_DIR = path.abspath('./tmp')
RESPONSE_DIR = TMP_DIR + '/' + 'resp'
PSRESTQUEUE_PUT = TMP_DIR + '/' + '5a682fbbe1bc487793d55fa09b55c547'
PSRESTQUEUE_GET = TMP_DIR + '/' + '95b51250d7ef4fcdaea1cf51886b8ba5'
PSRESTQUEUE_SRV = TMP_DIR + '/' + 'fcf29f8069d646e8bdc75af3eb7f02e4'
PSRESTQUEUE_WAIT = 250 #milliseconds

RESOURCE_DIR = path.abspath('./src/resources/')

#Logging preferences
LOG_LEVEL = 'INFO'
LOG_FILE = './psrest.log'
#get the os name
LOG_PLATFORM = platform.system()

#TODO: Sanitise the contents we get from the config file to prevent code injection.

def setup_credential_db():
    db = sqlite3.connect(CREDENTIAL_DATABASE)
    cursor = db.cursor()
    cursor.executescript("""
    CREATE TABLE client (cid INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, client_secret TEXT, name TEXT, description TEXT, authentication TEXT);
    CREATE TABLE refresh_client_map (rid INTEGER PRIMARY KEY AUTOINCREMENT, refresh_token TEXT, expiry REAL, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);
    CREATE TABLE action_client_map (aid INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);
    """
    )

def setup_metric_db():
    db = sqlite3.connect(METRIC_DATABASE)
    cursor = db.cursor()
    cursor.executescript("""
    CREATE TABLE metric (metric_id TEXT PRIMARY KEY, created REAL);
    CREATE TABLE label (label_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, metric_id TEXT, FOREIGN KEY(metric_id) REFERENCES metric(metric_id));
    """
    )