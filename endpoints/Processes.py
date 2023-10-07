import aiofiles
from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_500
from falcon.media.validators import jsonschema
from json import dumps
from configuration import PROCESS_SCHEMA
from log import LogClient, Message, Level, Code, Metric, Label
from auth import Authorisation, AuthorisationSchema
from entities import ProcessorConnection
from errors import InvalidToken, UnAuthorised, InvalidCredentials, ProcessorException

class Processes(object):
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
        
        except Exception as e:
            self.logger.record(Metric(Label.UNEXPECTED_ERROR))
            resp.status = HTTP_500
            resp.content_type = 'application/json'
            resp.text = dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))

    @jsonschema.validate(PROCESS_SCHEMA)    
    async def on_delete(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))
        resp.content_type = 'application/json'

        try:
            auth_token = self.auth.get_token(req)
            self.auth.is_authorised(auth_token, 'kill', AuthorisationSchema.BASIC)
            ticket: str = (await req.get_media()).pop('ticket')

            reader, writer = await (ProcessorConnection()).connect()
            writer.write(b'k' + ticket.encode("utf-8"))
            await writer.drain()
            if(await reader.read(1) != b'0'):
                writer.close()
                raise ProcessorException('Failed to cancel requested command. Either it doesn\'t exists or it has already completed.')

            resp.status = HTTP_200
            resp.text = dumps({'title': 'Success', 'description': 'Cmdlet execution cancelled.'})

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
