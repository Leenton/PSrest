from exceptions.PSRExceptions import *
from RestParser import *
from PSParser import *
from entities.Cmdlet import Cmdlet
from entities.CmdletLibrary import CmdletLibrary
from endpoints.OAuth import validate
from processing.PSScheduler import PSScheduler 
from processing.PSResponseStorage import PSResponseStorage
import json
from Config import *
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_403, HTTP_408, HTTP_500

#endpoint that gets called to actually execute the commands we want to execute with our application.

class Run(object):
    def __init__(self) -> None:
        self.scheduler = PSScheduler()
        self.response_storage = PSResponseStorage(S3SERVER, S3ACCESSKEY, S3SECRETKEY)
        # self.logger = Logger(log_queue, 1)
        self.cmdlet_library = CmdletLibrary()

    async def on_post(self, req, resp):
        resp.content_type = 'application/json'
        try:
            command = Cmdlet(
                self.cmdlet_library,
                (await req.get_media()),
                req.get_header('PLATFORM') or None,
                req.get_header('PSVERSION') or None,
                req.get_header('TTL') or None
            )

            token = req.get_header('ACCESS-TOKEN') or None
            if(validate(token, command.function)):
                ticket = await self.scheduler.request(command)
                resp.status = HTTP_200
                resp.text = (await self.response_storage.get(ticket)).data
                await self.response_storage.delete(ticket)
            else:
                resp.status = HTTP_403
                resp.text = json.dumps({'error': 'You are not authorised to run this command'})

        except (
            UnSuppotedPSVersion,
            UnSupportedPlatform,
            InvalidToken,
            UnkownCmdlet,
            InvalidCmdletParameter,
            ) as e:
            resp.status = HTTP_400
            resp.text = json.dumps({'error': e.message})

        except UnAuthorised as e:
            resp.status = HTTP_401
            resp.text = json.dumps({'error': e.message})
        
        except (CmdletExecutionTimeout, ExpiredPSTicket) as e:
            resp.status = HTTP_408
            resp.text = json.dumps({'error': e.message})

        except Exception as e:
            resp.status = HTTP_500
            resp.text = json.dumps({'error': 'Something went wrong!.'})
            print(e) 
