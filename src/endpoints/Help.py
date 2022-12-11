#help endopoint wich generates Powershell help for the command you asked for. This should probably use the PSProcessor to query for help if it has not been found in a cache
#we nuke the cache for any module that gets an update.
from RestParser import *

class Help(object):
    async def on_get(self, req, resp, command = None):
        if command: 
            
             #return just the default documentation for the application
            pass

        else: 

            #logic to find out what command we are talking about, and to fish out it's help
            pass