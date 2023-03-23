from exceptions.PSRExceptions import *
from RestParser import *
from PSParser import *
from entities.Cmdlet import Cmdlet
from endpoints.OAuth import validate_token
from processing.PSScheduler import PSScheduler 
from processing.PSResponseStorage import PSResponseStorage
from entities.Logger import Logger
from falcon.status_codes import * 
#endpoint that gets called to actually execute the commands we want to execute with our application.

class Run(object):
    def __init__(self) -> None:
        self.scheduler = PSScheduler()
        self.response_storage = PSResponseStorage()
        self.logger = Logger('log.txt', 'info')

    async def run(self, command, req = None):
        try:
            command = Cmdlet(
                req.getHeader('PLATFORM'),
                req.getHeader('PSVERSION'),
                req.getHeader('RUNAS'),
                parse(command),
                req.getHeader('TTL')
            )

            if(validate_token(req.get_header('ACCESS-TOKEN'), command.function, command.runas)):
                ticket = self.scheduler.request(command)
                if(ticket):
                    response = await self.response_storage.get(ticket)
                    return serialize(response)
                raise Exception('Failed to schedule command')

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

        except Exception as e:
            #Return a 500 error
            return serialize(e)

    async def on_post(self, req, resp):
        command = await req.get_media()
        reponse = self.run(command, req)