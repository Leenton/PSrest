import json
# import language builtins and 3rd party modules
from multiprocessing import Queue
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_403, HTTP_408, HTTP_500
from falcon.media.validators import jsonschema
from os import unlink
import asyncio
import math

# import project dependencies
from exceptions.PSRExceptions import *
from entities.Cmdlet import *
from entities.CmdletLibrary import CmdletLibrary
from entities.PSRestResponseStream import PSRestResponseStream
from entities.Schema import RUN_SCHEMA
from entities.OAuthService import OAuthService
from processing.PSProcessor import PSProcessor
from psrlogging.RecorderLogger import MetricRecorderLogger
from psrlogging.LogMessage import LogMessage
from psrlogging.Logger import LogLevel, LogCode
from configuration.Config import *

class Run(object):
    def __init__(self, kill: Queue, requests: Queue, alerts: Queue, stats: Queue, processes: Queue, logger: MetricRecorderLogger) -> None:
        self.processor = PSProcessor(kill, requests, alerts, stats, processes)
        self.cmdlet_library = CmdletLibrary()
        self.oauth = OAuthService()
        self.logger = logger
    
    # @jsonschema.validate(RUN_SCHEMA)
    async def on_post(self, req, resp):
        resp.content_type = 'application/json'
       
        try:
            ttl = req.get_header('TTL')
            if ttl is None:
                pass
            elif (ttl) > MAX_TTL:
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

            # self.oauth.validate_action(req.get_header('Authorization') or '', command.function)
            ticket = await self.processor.request(command)
            resp.status = HTTP_200

            stream = PSRestResponseStream(ticket, self.processor)
            try:
                await stream.open()
                resp.content_length = await stream.get_length()
                resp.stream = stream.read()
            except StreamTimeout as e:
                await stream.close(True)
                raise ExpiredPSTicket(ticket, 'Time out occurred waiting for PSProcessor to return the response.')

        except (
            UnSuppotedPSVersion,
            UnSupportedPlatform,
            UnkownCmdlet,
            InvalidCmdlet,
            InvalidCmdletParameter
            ) as e:
            resp.status = HTTP_400
            resp.text = json.dumps({'title': 'Request data failed validation', 'description': e.message})

        except InvalidToken as e:
            resp.status = HTTP_401
            resp.text = json.dumps({'title': 'Unauthorized Request', 'description': e.message})
        
        except UnAuthorised as e:
            resp.status = HTTP_403
            resp.text = json.dumps({'title': 'Forbidden Request', 'description': e.message})
        
        except ExpiredPSTicket as e:
            resp.status = HTTP_408
            resp.text = json.dumps({'title': 'Request Timeout', 'description': e.message})
        
        except (
            SchedulerException,
            PSRQueueException
            ) as e:
            resp.status = HTTP_500
            resp.text = json.dumps({'title': 'Internal Server Error', 'description': e.message})
            self.logger.log(LogMessage(message=e, level=LogLevel.ERROR, code='500'))

        except Exception as e:
            print(e)
            resp.status = HTTP_500
            resp.text = json.dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(LogMessage(message=e, level=LogLevel.ERROR, code=LogCode.SYSTEM))

    async def cleanup(self, ticket: PSTicket):
        tries = 1
        backoff = 0.001
        while(tries <= 5):
            try:
                unlink(RESPONSE_DIR + f'./{ticket.id}')
                break
            except FileNotFoundError:
                tries += 1
                await asyncio.sleep(backoff*(math.factorial(tries)))
                break
        if(tries >= 5):
            self.logger.log(LogMessage(message=f'Failed to delete {ticket.id} after 5 tries.', level=LogLevel.ERROR, code=LogCode.SYSTEM))