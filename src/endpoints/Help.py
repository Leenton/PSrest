#help endopoint wich generates Powershell help for the command you asked for. This should probably use the PSProcessor to query for help if it has not been found in a cache
#we nuke the cache for any module that gets an update.
from RestParser import *
from processing.PSScheduler import PSScheduler 
from processing.PSResponseStorage import PSResponseStorage
from PSParser import *
from Config import *

def get_help(command):
    #On application start up we should load all the modules we want to support into memory
    #and then cache the help for each command in the module.
    #This will allow us to return the help for a command without having to load the module
    #into memory.

    #return raw get help for the command from the module
    pass

class Help(object):
    def __init__(self) -> None:
        self.scheduler = PSScheduler()
        self.response_storage = PSResponseStorage()

    async def on_get(self, req, resp, command = None):
        if command: 
            command = command.lower()
            if command in get_allowed_commands():
                cmdlet = Cmdlet(
                    None,
                    None,
                    None,
                    parse("Get-Help -Name " + command + " -Full"),
                    CMDLT_TTL
                )
                ticket = self.scheduler.request(cmdlet)
                
                if(ticket):
                    response = await self.response_storage.get(ticket)
                    return serialize(response)
                
                raise Exception('Failed to schedule command')
            else: 
                #if the command is not in the allowed commands list then return a forbidden error
                pass
        else: 
            #if the help page has been disabled in the config file then return a forbiden error

            #return just the default documentation for the application
            pass

def get_allowed_commands():
    #return a list of all the commands that are allowed to be executed
    #this should be a list of all the commands that are in the allowed modules minus the commands that are not allowed

    #get all the commands in the allowed modules


    return 