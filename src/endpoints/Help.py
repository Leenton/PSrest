#help endopoint wich generates Powershell help for the command you asked for. This should probably use the PSProcessor to query for help if it has not been found in a cache
#we nuke the cache for any module that gets an update.
from Config import *
from entities.CmdletLibrary import CmdletLibrary
from falcon.status_codes import HTTP_200, HTTP_403, HTTP_404, HTTP_500
import json 

class Help(object):
    def __init__(self) -> None:
        self.cmdlet_library = CmdletLibrary()

    async def on_get(self, req, resp, command = None):
        if command and HELP: 
            #check command is a valid string and escape any SQL injection attempts

            if(isinstance(command, str)):
                info = self.cmdlet_library.get_cmdlet(command.lower())
                if(info):
                    resp.status = HTTP_200
                    resp.content_type = 'text/html'
                    resp.text = info.help
                else:
                    resp.status = HTTP_404
                    resp.content_type = 'application/json'
                    resp.text = json.dumps({'error': 'Page not found'})
            else:
                    resp.status = HTTP_500
                    resp.content_type = 'application/json'
                    resp.text = json.dumps({'error': 'Something went wrong!.'})
        else:
            if(not HELP):
                #Replace this with the fancy 500 error page
                resp.status = HTTP_403
                resp.content_type = 'application/json'
                resp.text = json.dumps({'error': 'Forbidden, help is disabled by the server'})
            
            #Replace this with the fancy help page
            resp.status = HTTP_200
            resp.content_type = 'text/html'
            resp.text = "PLAIN OLD DOCUMENTATION"