from falcon.status_codes import HTTP_200, HTTP_401, HTTP_500
from json import loads, dumps
from asyncio import sleep
from falcon.asgi import SSEvent
from typing import Generator, List
from uuid import uuid4
from datetime import datetime
from log import LogClient, Message, Level, Code, Metric, Label
from entities import ProcessorConnection
from processing import ResourceMonitor
from auth import Authorisation, AuthorisationSchema
from errors import InvalidToken, UnAuthorised, InvalidCredentials

class Events(object):
    def __init__(self, logger: LogClient) -> None:
        self.logger = logger
        self.resource_monitor = ResourceMonitor()
        self.auth = Authorisation()

    async def get_processes(self,) -> Generator[List[dict], None, None]:
        while True:
            await sleep(0.25)
            reader, writer = await (ProcessorConnection()).connect()
            writer.write(b'p')
            await writer.drain()
            snapshot = loads((await reader.read()).decode('utf-8'))
            writer.close()

            yield SSEvent(event="message", event_id=str(uuid4()), json=(snapshot), retry=2500)

    async def get_utilisation(self, time_range: int = 300) -> Generator[dict, None, None]:
        while True:
            await sleep(1)
            start = int(datetime.timestamp(datetime.now()))
            end = start - time_range
            metrics = await self.resource_monitor.get_utilisation(start, end)

            yield SSEvent(event="message", event_id=str(uuid4()), json=(metrics), retry=5000)

    async def on_get(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))

        try:
            auth_token = self.auth.get_token(req)
            self.auth.is_authorised(auth_token, 'view', AuthorisationSchema.BASIC)
            event_type = req.params.get('t', None)

            match event_type:
                case 'processes':
                    stream = self.get_processes()
                case 'utilisation':
                    stream = self.get_utilisation()
                case _:
                    raise Exception('Invalid event type.')

            resp.status = HTTP_200
            resp.content_type = 'text/event-stream'
            resp.sse = stream
        
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