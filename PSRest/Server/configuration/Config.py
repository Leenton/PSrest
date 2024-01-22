# import dependecies for reading the config file. 
import platform
import sqlite3
from os import path, mkdir
from secrets import token_bytes
from pathlib import Path
from shutil import copyfile
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from json import load
from .Schema import CONFIG_SCHEMA
from os import getenv, path, listdir
from entities import VersionNumber

# PSRestVersion
VERSION = '1.0.0'

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
if(not path.isfile(APP_DATA + '/config.json')):
    copyfile(str(Path(__file__).parent) + '/DefaultConfig.json', APP_DATA + '/config.json')

CONFIG: dict = load(open(APP_DATA + '/config.json', 'r'))
try:
    validate(
        instance=CONFIG,
        schema=CONFIG_SCHEMA
    )
except ValidationError as e:
    raise Exception('Invalid config file. Please check the config file against the schema. ' + e.message)

CONFIG_FILE = APP_DATA + '/config.json'
PORT = CONFIG['Port']
CERTIFICATE = CONFIG.get('SSLCertificate')
KEY_FILE = CONFIG.get('SSLKeyFile')
KEYFILE_PASSWORD = getenv('PSRestSSLKeyFilePassword') if KEY_FILE and CERTIFICATE else None

CIPHERS =  CONFIG.get('SSLCiphers') if CONFIG.get('SSLCiphers') else 'TLSv1' 

# Constants for the ticketing system
DEFAULT_TTL = CONFIG['DefaultTTL']
MAX_TTL = CONFIG['MaxTTL']
STRICT_TTL = CONFIG['StrictTTL']
ACCESS_TOKEN_TTL = 3600
REFRESH_TOKEN_TTL = 86400 * 14

# Constants for how we serve responses
DEFAULT_DEPTH = CONFIG['DefaultDepth']
STRICT_DEPTH = CONFIG['StrictDepth']
MAX_DEPTH = 100
TOO_LONG = 0.25

# Constants for the powershell execution
PS_PROCESSORS = 16
MAX_PROCESSES = 32
PROCESSOR_TICK_RATE = 5000
PROCESSOR_SPIN_UP_PERIOD = 0.25
PROCESSOR_SPIN_DOWN_PERIOD = 5
ARBITRARY_COMMANDS = CONFIG['ArbitraryCommands']
HELP = CONFIG['Help']
PSREST_CMDLETS = [
    'Get-PSRestConfiguration',
    'Set-PSRestConfiguration',
    'Update-PSRest',
    'Start-PSRest',
    'New-PSRestApplication',
    'Set-PSRestApplication',
    'Get-PSRestApplication',
    'Remove-PSRestApplication'
]
DOCS = CONFIG['Docs']
COMPETED = 'completed'
FAILED = 'failed'

# Constants for storage and socket communication
TMP_DIR = APP_DATA + '/temp'
if(not path.isdir(TMP_DIR)):
    mkdir(TMP_DIR)
PROCESSOR_HOST = '127.0.0.1'
PSREST_PORT = 27500
INGESTER_ADDRESS = f"{PROCESSOR_HOST}:{PSREST_PORT}"
INGESTER_UNIX_ADDRESS = TMP_DIR + '/' + '95b51250d7ef4fcdaea1cf51886b8ba5'
RESOURCE_DIR = str(Path(__file__).parent.parent) + '/resources'
PATCH_DIR = str(Path(__file__).parent.parent) + '/configuration/patches'

# Logging preferences
LOG_LEVEL = 'info'
LOG_FILE = APP_DATA + '/PSRest.log'

# Constants for the encryption/fingerprinting
# Read the secret file for the encryption key
if(not path.isfile(APP_DATA + '/zvakavanzika')):
    with open(APP_DATA + '/zvakavanzika', 'wb') as f:
        f.write(token_bytes(32))

with open(APP_DATA + '/zvakavanzika', 'rb') as f:
    SECRET_KEY = (f.read()).decode()

CREDENTIAL_DATABASE = APP_DATA + '/data.db' # OAuth2 credential database

def setup_credential_database():
    # Check if the databases exists if not create them
    if(not path.exists(CREDENTIAL_DATABASE)):
        db = sqlite3.connect(CREDENTIAL_DATABASE)
        cursor = db.cursor()
        cursor.executescript(
            """--sql
            CREATE TABLE client (cid INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, client_secret TEXT, name TEXT, description TEXT, authentication TEXT, enabled_cmdlets TEXT, disabled_cmdlets TEXT, enabled_modules TEXT);
            CREATE TABLE refresh_client_map (rid INTEGER PRIMARY KEY AUTOINCREMENT, refresh_token TEXT, expiry REAL, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);
            CREATE TABLE version (version TEXT);
            """
        )

        cursor.execute("INSERT INTO version (version) VALUES (?)", (VERSION,))
        db.commit()

        DB_VERSION = VERSION
    else:
        db = sqlite3.connect(CREDENTIAL_DATABASE)
        cursor = db.cursor()
        cursor.execute("SELECT version FROM version")
        DB_VERSION = cursor.fetchone()[0]
        db.close()

    if(VersionNumber(DB_VERSION) < VersionNumber(VERSION)):
        # Get all the patches in the patches folder greater than the current version
        patches = listdir(PATCH_DIR)
        patches = [patch for patch in patches if VersionNumber(patch.split('.sql')[0]) > VersionNumber(DB_VERSION)]
        patches.sort()

        for patch in patches:
            db = sqlite3.connect(CREDENTIAL_DATABASE)
            cursor = db.cursor()
            cursor.executescript(open(PATCH_DIR + '/' + patch, 'r').read())
            cursor.execute("UPDATE version SET version = ?", (patch.split('.sql')[0],))
            db.commit()
            db.close()
