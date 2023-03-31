from exceptions.PSRExceptions import *
from RestParser import *
from PSParser import *
from entities.Cmdlet import Cmdlet
from entities.CmdletLibrary import CmdletLibrary
from endpoints.OAuth import validate
from processing.PSScheduler import PSScheduler 
from processing.PSResponseStorage import PSResponseStorage
from falcon.status_codes import * 
import json

#endpoint that gets called to actually execute the commands we want to execute with our application.

class Run(object):
    def __init__(self) -> None:
        self.scheduler = PSScheduler()
        self.response_storage = PSResponseStorage()
        # self.logger = Logger(log_queue, 1)
        self.cmdlet_library = CmdletLibrary()

    async def run(self, command, req = None):
        try:
            command = Cmdlet(
                self.cmdlet_library,
                command,
                req.get_header('PLATFORM') or None,
                req.get_header('PSVERSION') or None,
                req.get_header('TTL') or None
            )

            token = req.get_header('ACCESS-TOKEN') or None
            if(validate(token, command.function)):
                ticket = await self.scheduler.request(command)
                if(ticket):
                    try:
                        response = await self.response_storage.get(ticket)
                    except Exception as e:
                        raise Exception('Command timed out before response was received')
                    return serialize(response)
                raise Exception('Failed to schedule command')
            else:
                print("WTF?")

        except (
            UnAuthenticated,
            UnSuppotedPSVersion,
            UnSupportedPlatform,
            InvalidToken,
            UnkownCmdlet,
            InvalidCmdletParameter,
            ) as e:
            #Return a 400 error
            return serialize(e)
        
        except UnAuthorised as e:
            #Return a 401 error
            return serialize(e)
        
        except CmdletExecutionTimeout as e:
            #Return a 408 error
            return serialize(e)

        # except Exception as e:
        #     #Return a 500 error
        #     return serialize(e)

    async def on_post(self, req, resp):
        command = await req.get_media()
        reponse = await self.run(command, req)