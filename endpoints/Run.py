from json import dumps
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_403, HTTP_408, HTTP_500, HTTP_503
from falcon.media.validators import jsonschema
import traceback
from configuration import (
    DEFAULT_TTL,
    DEFAULT_DEPTH,
    MAX_TTL,
    MAX_DEPTH,
    RUN_SCHEMA
)
from errors import (
    InvalidToken,
    UnAuthorised,
    ProcessorException,
    SchedulerException,
    StreamTimeout,
    UnSuppotedPSVersion,
    UnSupportedPlatform,
    InvalidCmdlet,
    UnkownCmdlet,
    InvalidCmdletParameter
)
from entities.Cmdlet import Cmdlet, CmdletInfoLibrary
from processing import OAuthService
from log import LogClient, Message, Level, Code, Metric, Label

class Run(object):
    def __init__(self, logger: LogClient) -> None:
        self.cmdlet_library = CmdletInfoLibrary()
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
            
            elif depth <= 0:
                raise InvalidCmdlet(f'Depth must be greater than 0.')

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
        self.logger.record(Metric(Label.REQUEST))
        resp.content_type = 'application/json'
        
        try:
            ttl, depth, header = self.validate_headers(req)
            command = Cmdlet( self.cmdlet_library, (await req.get_media()), ttl, depth)

            # command.application_name = self.oauth.get_authorized_application_name(header, command.function)

            response = await command.invoke()

            resp.status =  HTTP_200
            resp.content_length = await response.get_length()
            resp.stream = response.get_content()

        except (
            UnSuppotedPSVersion,
            UnSupportedPlatform,
            UnkownCmdlet,
            InvalidCmdlet,
            InvalidCmdletParameter
        ) as e:
            resp.status = HTTP_400
            resp.text = dumps({'title': 'Request data failed validation', 'description': e.message})

        except InvalidToken as e:
            self.logger.record(Metric(Label.INVALID_CREDENTIALS_ERROR))
            resp.status = HTTP_401
            resp.text = dumps({'title': 'Unauthorised Request', 'description': e.message})
        
        except UnAuthorised as e:
            self.logger.record(Metric(Label.UNAUTHORISED_ERROR))
            resp.status = HTTP_403
            resp.text = dumps({'title': 'Forbidden Request', 'description': e.message})
        
        except StreamTimeout as e:
            resp.status = HTTP_408
            resp.text = dumps({'title': 'Request Timeout', 'description': 'Time out occurred waiting for PSProcessor to return the response.'})

        except ProcessorException as e:
            if e.message == 'Too busy.':
                self.logger.record(Metric(Label.DROPPED_REQUEST))
                resp.status = HTTP_503
                resp.text = dumps({
                    'title': 'Too Many Requests',
                    'description': 'The server is currently unable to handle the request due to a temporary overload, please try again later.'
                    })
            else:
                resp.status = HTTP_500
                resp.text = dumps({'title': 'Internal Server Error', 'description': e.message})
                self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))
        
        except (
            SchedulerException,
        ) as e:
            resp.status = HTTP_500
            resp.text = dumps({'title': 'Internal Server Error', 'description': e.message})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))

        except Exception as e:
            print(e)
            traceback.print_exc()
            resp.status = HTTP_500
            resp.text = dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))