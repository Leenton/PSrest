import aiofiles
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_500
from falcon.media.validators import jsonschema
from json import dumps
from configuration import PROCESS_SCHEMA
from log import LogClient, Message, Level, Code, Metric, Label
from auth import Authorisation, AuthorisationSchema
from entities import ProcessorConnection
from errors import InvalidToken, UnAuthorised, InvalidCredentials, ProcessorException, InvalidTicket

class Processes(object):
    """
    Handles HTTP GET and DELETE requests for the processes endpoint. This endpoint
    provided a task manager like interface for viewing and killing running cmdlets.

    Attributes:
        logger (LogClient): A client for logging messages and metrics.
        auth (Authorisation): An object that handles authentication and authorization.

    Methods:
        on_get: Serves the processes.html page if the user is authorized to view it.
        on_delete: When a HTTP DELETE request is received, it issues a command to the
            processor to cancel the cmdlet execution.
    """

    def __init__(self, logger: LogClient) -> None:
        self.logger = logger
        self.auth = Authorisation()

    def get(self):
        return {"message": "Processes endpoint"}
    
    async def on_get(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))

        try:
            auth_token = self.auth.get_token(req)
            self.auth.is_authorised(auth_token, 'view', AuthorisationSchema.BASIC)
            resp.status = HTTP_200
            resp.content_type = 'text/html'
            async with aiofiles.open('./resources/html/processes.html', 'rb') as f:
                resp.text = await f.read()

        except (
            InvalidToken,
            UnAuthorised,
            InvalidCredentials
        ) as e:
            self.logger.record(Metric(Label.INVALID_CREDENTIALS_ERROR))
            resp.status = HTTP_401
            resp.content_type = 'application/json'
            resp.text = dumps({'title': 'Unauthorised Request', 'description': e.message})
            resp.append_header('WWW-Authenticate', 'Basic realm=<realm>, charset="UTF-8"')
        
        except Exception as e:
            self.logger.record(Metric(Label.UNEXPECTED_ERROR))
            resp.status = HTTP_500
            resp.content_type = 'application/json'
            resp.text = dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))
 
    async def on_delete(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))
        resp.content_type = 'application/json'

        try:
            auth_token = self.auth.get_token(req)
            self.auth.is_authorised(auth_token, 'kill', AuthorisationSchema.BASIC)
            ticket = req.params.get('ticket', None)
            if(ticket == None or not isinstance(ticket, str) or len(ticket) != 32):
                raise InvalidTicket('The ticket provided is invalid.')

            reader, writer = await (ProcessorConnection()).connect()
            writer.write(b'k' + ticket.encode("utf-8"))
            await writer.drain()
            if(await reader.read(1) != b'0'):
                writer.close()
                raise ProcessorException('Failed to cancel requested command. Either it doesn\'t exist or it has already completed.')

            resp.status = HTTP_200
            resp.text = dumps({'title': 'Success', 'description': 'Cmdlet execution cancelled.'})

        except InvalidTicket as e:
            self.logger.record(Metric(Label.BAD_REQUEST_ERROR))
            resp.status = HTTP_400
            resp.text = dumps({'title': 'Bad Request', 'description': e.message})
        
        except (
            InvalidToken,
            UnAuthorised,
            InvalidCredentials
        ) as e:
            self.logger.record(Metric(Label.INVALID_CREDENTIALS_ERROR))
            resp.status = HTTP_401
            resp.text = dumps({'title': 'Unauthorised Request', 'description': e.message})
            resp.append_header('WWW-Authenticate', 'Basic realm=<realm>, charset="UTF-8"')
        
        except ProcessorException as e:
            self.logger.record(Metric(Label.UNEXPECTED_ERROR))
            resp.status = HTTP_500
            resp.text = dumps({'title': 'Internal Server Error', 'description': e.message})

        except Exception as e:
            self.logger.record(Metric(Label.UNEXPECTED_ERROR))
            resp.status = HTTP_500
            resp.text = dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))
