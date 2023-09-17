import json
# import language builtins and 3rd party modules
from multiprocessing import Queue
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_403, HTTP_408, HTTP_500, HTTP_503
from falcon.media.validators import jsonschema

# import project dependencies
from exceptions.PSRExceptions import *
from entities.Cmdlet import *
from entities.CmdletLibrary import CmdletLibrary
from entities.PSRestResponseStream import PSRestResponseStream
from entities.Schema import RUN_SCHEMA
from entities.OAuthService import OAuthService
from processing.PSProcessor import PSProcessor
from log.LogMessage import LogMessage, LogLevel, LogCode
from log.Metric import Metric, MetricLabel
from log.MetricRecorderLogger import MetricRecorderLogger
from configuration.Config import *
import traceback

class Run(object):
    def __init__(self, processor: PSProcessor, logger: MetricRecorderLogger) -> None:
        self.processor = processor
        self.cmdlet_library = CmdletLibrary()
        self.oauth = OAuthService()
        self.logger = logger

    def validate_headers(self, req):
        try:
            ttl = req.get_header('TTL')

            if ttl == None:
                ttl = int(DEFAULT_TTL)
                
            elif ttl > MAX_TTL:
                raise InvalidCmdlet(f'TTL is too long. Please use a value less than {MAX_TTL} seconds.')
            
        except (ValueError, TypeError):
            raise InvalidCmdlet(f'TTL is not a valid number. Please use a value less than {MAX_TTL} seconds.')

        try:
            depth = req.get_header('Depth')

            if depth == None:
                depth = int(DEFAULT_DEPTH)

            elif depth > int(MAX_DEPTH):
                raise InvalidCmdlet(f'Depth is too long. Please use a value less than {MAX_DEPTH}.')
            
        except (ValueError, TypeError):
            raise InvalidCmdlet(f'Depth is not a valid number. Please use a value less than {MAX_DEPTH}.')
        
        header = req.get_header('Authorization')
        if header == None:
            header = ''
        elif not isinstance(header, str):
            header = 'true'

        return ttl, depth, header

    @jsonschema.validate(RUN_SCHEMA)
    async def on_post(self, req, resp):
        self.logger.record(Metric(MetricLabel.REQUEST))
        resp.content_type = 'application/json'
        
        try:
            ttl, depth, header = self.validate_headers(req)
            command = Cmdlet( self.cmdlet_library, (await req.get_media()), ttl, depth)

            # self.oauth.validate_action(header, command.function)

            ticket = await self.processor.request(command)
            stream = PSRestResponseStream(ticket, self.processor)
        
            await stream.open()

            resp.status = HTTP_200
            resp.content_length = await stream.get_length()
            resp.stream = stream.read()


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
            self.logger.record(Metric(MetricLabel.INVALID_CREDENTIALS_ERROR))
            resp.status = HTTP_401
            resp.text = json.dumps({'title': 'Unauthorised Request', 'description': e.message})
        
        except UnAuthorised as e:
            self.logger.record(Metric(MetricLabel.UNAUTHORISED_ERROR))
            resp.status = HTTP_403
            resp.text = json.dumps({'title': 'Forbidden Request', 'description': e.message})
        
        except StreamTimeout as e:
            resp.status = HTTP_408
            resp.text = json.dumps({'title': 'Request Timeout', 'description': 'Time out occurred waiting for PSProcessor to return the response.'})

        except ProcessorException as e:
            if e.message == 'Too busy.':
                self.logger.record(Metric(MetricLabel.DROPPED_REQUEST))
                resp.status = HTTP_503
                resp.text = json.dumps({
                    'title': 'Too Many Requests',
                    'description': 'The server is currently unable to handle the request due to a temporary overload, please try again later.'
                    })
            else:
                resp.status = HTTP_500
                resp.text = json.dumps({'title': 'Internal Server Error', 'description': e.message})
                self.logger.log(LogMessage(message=e, level=LogLevel.ERROR, code='500'))
        
        except (
            SchedulerException,
            ) as e:
            resp.status = HTTP_500
            resp.text = json.dumps({'title': 'Internal Server Error', 'description': e.message})
            self.logger.log(LogMessage(message=e, level=LogLevel.ERROR, code='500'))

        except Exception as e:
            print(e)
            traceback.print_exc()
            resp.status = HTTP_500
            resp.text = json.dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(LogMessage(message=e, level=LogLevel.ERROR, code=LogCode.SYSTEM))