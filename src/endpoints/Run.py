from exceptions.PSRExceptions import *
from RestParser import *
from PSParser import *
import aiofiles
from entities.Cmdlet import *
from entities.CmdletLibrary import CmdletLibrary
from entities.PSRestResponseStream import PSRestResponseStream
from endpoints.OAuth import validate
from processing.PSProcessor import PSProcessor
import json
from queue import Queue 
from Config import *
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_403, HTTP_408, HTTP_500
from falcon.media.validators import jsonschema
from entities.Schema import RUN_SCHEMA

class Run(object):
    def __init__(self, kill: Queue, requests: Queue, alerts: Queue) -> None:
        self.processor = PSProcessor(kill, requests, alerts)
        self.cmdlet_library = CmdletLibrary()
    
    @jsonschema.validate(RUN_SCHEMA)
    async def on_post(self, req, resp):
        resp.content_type = 'application/json'
       
        try:
            ttl = req.get_header('TTL')
            if ttl is None:
                pass
            elif (ttl) > int(MAX_TTL):
                raise InvalidCmdlet(f'TTL is too long. Please use a value less than {MAX_TTL} seconds.')
        except (ValueError, TypeError):
            raise InvalidCmdlet(f'TTL is not a valid number. Please use a value less than {MAX_TTL} seconds.')

        try:
            depth = req.get_header('DEPTH')
            if depth is None:
                pass
            elif (depth) > int(MAX_DEPTH):
                raise InvalidCmdlet(f'DEPTH is too long. Please use a value less than {MAX_DEPTH}.')
        except (ValueError, TypeError):
            raise InvalidCmdlet(f'DEPTH is not a valid number. Please use a value less than {MAX_DEPTH}.')
        
        try:
            command: Cmdlet = Cmdlet(
                self.cmdlet_library,
                (await req.get_media()),
                ttl or int(DEFAULT_TTL),
                depth or int(DEFAULT_DEPTH)
            )

            token = req.get_header('ACCESS-TOKEN') or None
            if(validate(token, command.function)):
                ticket = await self.processor.request(command)
                resp.status = HTTP_200

                try:
                    stream = PSRestResponseStream(ticket)
                    resp.content_length = stream.length
                    resp.stream = stream.read()
                except Exception as e:
                    raise ExpiredPSTicket(ticket, 'Time out occurred waiting for PSProcessor to return the response.')
            else:
                resp.status = HTTP_403
                resp.text = json.dumps({'error': 'You are not authorised to run this command'})

        except (
            UnSuppotedPSVersion,
            UnSupportedPlatform,
            InvalidToken,
            UnkownCmdlet,
            InvalidCmdlet,
            InvalidCmdletParameter
            ) as e:
            resp.status = HTTP_400
            resp.text = json.dumps({'error': e.message})

        except UnAuthorised as e:
            resp.status = HTTP_401
            resp.text = json.dumps({'error': e.message})
        
        except ExpiredPSTicket as e:
            resp.status = HTTP_408
            resp.text = json.dumps({'error': e.message})
        
        except (
            SchedulerException,
            PSRQueueException
            ) as e:
            resp.status = HTTP_500
            resp.text = json.dumps({'error': e.message})

        except Exception as e:
            resp.status = HTTP_500
            resp.text = json.dumps({'error': 'Something went wrong!.'})
            print(e) 
