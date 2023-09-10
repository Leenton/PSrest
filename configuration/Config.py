# import dependecies for reading the config file. 
import configparser
import platform
import random
import sqlite3
from os import path, remove, mkdir
from secrets import token_bytes
from pathlib import Path
from time import sleep
from shutil import copyfile

# PSRestVersion
VERSION = '0.1.1'

# Constants for the platform
PLATFORM = platform.system()

if(PLATFORM == 'Windows'):
    APP_DATA = path.expanduser("~/AppData/Roaming/PSRest")
elif(PLATFORM == 'Linux'):
    APP_DATA = path.expanduser("~/.config/PSRest")
elif(PLATFORM == 'Darwin'):
    APP_DATA = path.expanduser("~/Library/Application Support/PSRest")
else:
    raise Exception('Unsupported OS platform')

if(not path.isdir(APP_DATA)):
    mkdir(APP_DATA)

# Load the config file and inject the values into the constants
if(not path.isfile(APP_DATA + '/config')):
    copyfile(str(Path(__file__).parent) + '/config', APP_DATA + '/config')

CONFIG = configparser.ConfigParser()      
CONFIG.read_file(open((APP_DATA + '/config'), 'r')) 
HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
PORT = int(CONFIG.get('Server', 'PORT'))

# Constants for the ticketing system
DEFAULT_TTL = CONFIG.get('TimeOut', 'DEFAULT_TTL')
MAX_TTL = int(CONFIG.get('TimeOut', 'MAX_TTL'))
ACCESS_TOKEN_TTL = 3600
REFRESH_TOKEN_TTL = 86400 * 14

# Constants for how we serve responses
DEFAULT_DEPTH = CONFIG.get('Response', 'DEFAULT_DEPTH')
MAX_DEPTH = 100
TOO_LONG = 0.25

# Constants for the powershell execution
PS_PROCESSORS = 8
MAX_PROCESSES = 33
PROCESSOR_TICK_RATE = 1000
PROCESSOR_SPIN_UP_PERIOD = 0.25
ARBITRARY_COMMANDS = True if ((CONFIG.get('PSExecution', 'ARBITRARY_COMMANDS')).lower() == 'true') else False
HELP = CONFIG.get('Help', 'HELP')
MODULES = CONFIG.get('ExposedModules', 'MODULES')
DISABLE_COMMANDS = CONFIG.get('DisableCmdlets', 'CMDLETS')
ENABLE_COMMANDS = CONFIG.get('EnableCmdlets', 'CMDLETS')
COMPETED = 'completed'
FAILED = 'failed'

# Constants for storage and socket communication
TMP_DIR = APP_DATA + '/temp'
if(not path.isdir(TMP_DIR)):
    mkdir(TMP_DIR)

RESPONSE_DIR = TMP_DIR + '/' + 'r'
if(not path.isdir(RESPONSE_DIR)):
    mkdir(RESPONSE_DIR)

CULL_DIR = TMP_DIR + '/' + 'c'
if(not path.isdir(CULL_DIR)):
    mkdir(CULL_DIR)

PSRESTQUEUE_PUT = TMP_DIR + '/' + '5a682fbbe1bc487793d55fa09b55c547'
PSRESTQUEUE_GET = TMP_DIR + '/' + '95b51250d7ef4fcdaea1cf51886b8ba5'
PSRESTQUEUE_SRV = TMP_DIR + '/' + 'fcf29f8069d646e8bdc75af3eb7f02e4'
PSRESTQUEUE_WAIT = 250 # milliseconds
RESOURCE_DIR = str(Path(__file__).parent.parent) + '/resources'

# Logging preferences
LOG_LEVEL = 'INFO'
LOG_FILE = APP_DATA + '/PSRest.log'

# Constants for the encryption/fingerprinting
# Read the secret file for the encryption key
if(not path.isfile(APP_DATA + '/zvakavanzika')):
    with open(APP_DATA + '/zvakavanzika', 'wb') as f:
        #  f.write(token_bytes(32))
        f.write('2ed154d0c89362da0e2fc49257c5fb27c01cdfbc85238ea334e84dbc8eccfee3812b41add4149999b2277780b0edbdda4905f46f607fd3ffd8d3601113c1e7ae'.encode())

with open(APP_DATA + '/zvakavanzika', 'rb') as f:
    SECRET_KEY = (f.read()).decode()

# These database files and the temp files should live in user space not in the project directory
CREDENTIAL_DATABASE = APP_DATA + '/data.db' # OAuth2 credential database
METRIC_DATABASE = TMP_DIR + '/metrics.db' # Metric database
PROCESSOR_DATABASE = TMP_DIR + '/processor.db' # Processor database

# TODO: Sanitise the contents we get from the config file to prevent code injection.

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
    CREATE TABLE labels (label_id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT, metric_id TEXT, FOREIGN KEY(metric_id) REFERENCES metric(metric_id));
    CREATE TABLE resource (resource_id INTEGER PRIMARY KEY AUTOINCREMENT, resource TEXT, value TEXT, created REAL);
    """
    )

def setup_processor_db():

    sleep(random.random())
    if(path.isfile(PROCESSOR_DATABASE)):
        remove(PROCESSOR_DATABASE)
    
    db = sqlite3.connect(PROCESSOR_DATABASE)
    cursor = db.cursor()
    # add a cascade to the schedule table so when a process is deleted, it's ticket is also deleted
    cursor.executescript("""
    CREATE TABLE PSProcessor (ticket TEXT PRIMARY KEY, pid TEXT, application TEXT, command TEXT, created REAL, expires REAL, modified REAL);
    CREATE TABLE PSProcess (pid TEXT PRIMARY KEY, last_seen REAL, FOREIGN KEY(pid) REFERENCES PSProcessor(pid) ON DELETE CASCADE);
    """
    )