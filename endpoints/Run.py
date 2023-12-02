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
from log import LogClient, Message, Level, Code
from auth import Authorisation
from auth import AuthorisationToken

class Run(object):
    """
    Handles HTTP POST requests to execute PowerShell cmdlets.

    Attributes:
        cmdlet_library (CmdletInfoLibrary): A library of PowerShell cmdlet information.
        authorisation (Authorisation): An object that handles authentication and authorization.
        logger (LogClient): A client for logging messages and metrics.

    Methods:
        validate_headers: Validates the request headers and returns the TTL and depth parameters.
        on_post: Handles HTTP POST requests to execute PowerShell cmdlets.
    """
    
    def __init__(self, logger: LogClient) -> None:
        self.cmdlet_library = CmdletInfoLibrary()
        self.authorisation = Authorisation()
        self.logger = logger

    async def validate_headers(self, req) -> tuple[int, int, AuthorisationToken]:
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
        
        token = self.authorisation.get_token(req)

        return ttl, depth, token

    @jsonschema.validate(RUN_SCHEMA)
    async def on_post(self, req, resp):
        resp.content_type = 'application/json'
        
        try:
            ttl, depth, token = self.validate_headers(req)

            response = await (Cmdlet(
                self.cmdlet_library,
                self.authorisation,
                (await req.get_media()),
                ttl,
                depth,
                token
            )).invoke()

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
            resp.status = HTTP_401
            resp.text = dumps({'title': 'Unauthorised Request', 'description': e.message})
        
        except UnAuthorised as e:
            resp.status = HTTP_403
            resp.text = dumps({'title': 'Forbidden Request', 'description': e.message})
        
        except StreamTimeout as e:
            resp.status = HTTP_408
            resp.text = dumps({'title': 'Request Timeout', 'description': 'Time out occurred waiting for PSProcessor to return the response.'})

        except ProcessorException as e:
            if e.message == 'Too busy.':
                resp.status = HTTP_503
                resp.text = dumps({
                    'title': 'Too Many Requests',
                    'description': 'The server is currently unable to handle the request due to a temporary overload, please try again later.'
                    })
            else:
                resp.status = HTTP_500
                resp.text = dumps({'title': 'Internal Server Error', 'description': e.message})
                self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))
        
        except SchedulerException as e:
            resp.status = HTTP_500
            resp.text = dumps({'title': 'Internal Server Error', 'description': e.message})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))

        except Exception as e:
            print(e)
            traceback.print_exc()
            resp.status = HTTP_500
            resp.text = dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))