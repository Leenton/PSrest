#help endopoint wich generates Powershell help for the command you asked for. This should probably use the PSProcessor to query for help if it has not been found in a cache
#we nuke the cache for any module that gets an update.
from Config import *
from entities.CmdletLibrary import CmdletLibrary


class Help(object):
    def __init__(self) -> None:
        self.cmdlet_library = CmdletLibrary()

    async def on_get(self, req, resp, command = None):
        if command and HELP: 
            #check command is a valid string and escape any SQL injection attempts

            if(isinstance(command, str)):
                info = self.cmdlet_library.get_cmdlet(command)
                if(info):
                    return info.help
                else:
                    raise Exception('Command not found')
            else:
                raise Exception('Invalid command provided')
        else:
            if(not HELP):
                raise Exception('forbidden')
            #if the help page has been disabled in the config file then return a forbiden error

            #return just the default documentation for the application
            pass
