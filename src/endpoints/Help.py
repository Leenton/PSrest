#help endopoint wich generates Powershell help for the command you asked for. This should probably use the PSProcessor to query for help if it has not been found in a cache
#we nuke the cache for any module that gets an update.
from RestParser import *

def get_help(command):
    #Check our local cache for the command. If the version of the command in cache is different than 
    #the version of the module currently installed, then refresh the cache with the new command.
    pass

class Help(object):
    async def on_get(self, req, resp, command = None):
        if command: 
            #logic to find out what command we are talking about, and to fish out it's help
            command = parse(command)    
            get_help(command.fucntion)
            pass

        else: 

             #return just the default documentation for the application
            pass
