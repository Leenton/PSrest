from falcon.status_codes import HTTP_200, HTTP_400, HTTP_401, HTTP_500
from json import loads, dumps
from random import randint
from asyncio import sleep
from falcon.asgi import SSEvent
from typing import Generator, List
from uuid import uuid4
from datetime import datetime
from log import LogClient, Message, Level, Code, Metric, Label
from entities import ProcessorConnection
from processing import ResourceMonitor
from auth import Authorisation, AuthorisationSchema
from errors import (
    InvalidToken,
    UnAuthorised,
    InvalidCredentials,
    InvalidTimeRange,
    InvalidEventType
)

class Events(object):
    """
    Generates streams of events related to running processes and resource utilization data.

    Attributes:
        logger (LogClient): A client for logging messages and metrics.
        resource_monitor (ResourceMonitor): A monitor for resource utilization data.
        auth (Authorisation): An object that handles authentication and authorization.

    Methods:
        get_processes: Generates a stream of events that represent running processes.
        get_utilisation: Generates a stream of resource utilization data.
    """
    def __init__(self, logger: LogClient) -> None:
        self.logger = logger
        self.resource_monitor = ResourceMonitor()
        self.auth = Authorisation()

    async def get_processes(self) -> Generator[List[dict], None, None]:
        while True:
            # reader, writer = await (ProcessorConnection()).connect()
            # writer.write(b'p')
            # await writer.drain()
            # snapshot = loads((await reader.read()).decode('utf-8'))
            # writer.close()
            snapshot = [
                {
                    'application_name': 'Leenton Service Desk',
                    'function': "Write-Host",
                    'ttl': randint(15, 101),
                    'created': 1696811259,
                    'pid': 'sqawdqwdqw',
                    'ticket': '12345678901234567890123456789012'
                },
                {
                    'application_name': 'Leenton Service Desk',
                    'function': "Get-Help",
                    'ttl': randint(15, 101),
                    'created': 1696815642,
                    'pid': None,
                    'Ticket': '123456789012mmmmmmmmmmmmmm789012'
                },
                {
                    'application_name': 'Leenton Service Desk',
                    'function': "New-ADUser",
                    'ttl': randint(15, 101),
                    'created': 1696809246,
                    'pid': 'Runnq12qd1w3d12ding',
                    'Ticket': '1234567890123456dddddddddd789012'
                },
                {
                    'application_name': 'Github Pages Action',
                    'function': "New-Deployment",
                    'ttl': randint(15, 101),
                    'created': 1696809246,
                    'pid': None,
                    'Ticket': '12345aaaaaa2345678901234567890a2'
                }
            ]

            yield SSEvent(event="message", event_id=str(uuid4()), json=(snapshot), retry=2500)
            await sleep(0.25)

    async def get_utilisation(self, time_range: int) -> Generator[dict, None, None]:
        for metric in (await self.resource_monitor.get_utilisation(time_range)):
            yield SSEvent(event="message", event_id=str(uuid4()), json=(metric), retry=5000)
            

    # async def get_utilisation(self, time_range: int) -> Generator[dict, None, None]:
    #     batch = True
    #     while True:
    #         start = int(datetime.timestamp(datetime.now()))

    #         if(batch):
    #             end = start
    #             resolution = 900
    #             sleep_for = 900
    #         else:
    #             end = start - time_range
    #             resolution = 1
            
    #         metrics = await self.resource_monitor.get_utilisation(start, end, resolution)
    #         metrics['created'] = start
    #         metrics['range'] = time_range
    #         batch = False

    #         yield SSEvent(event="message", event_id=str(uuid4()), json=(metrics), retry=5000)
        
    #         await sleep(1)

    async def on_get(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))

        try:
            auth_token = self.auth.get_token(req)
            self.auth.is_authorised(auth_token, 'view', AuthorisationSchema.BASIC)
            event_type = req.params.get('t', None)
            time_range: str = req.params.get('r', '300')

            if(time_range.isnumeric()):
                time_range = int(time_range)

            if(not isinstance(time_range, int) or time_range < 60 or time_range > 86400 * 31):
                raise InvalidTimeRange('The time range provided is invalid. It must be an integer between 60 and 2678400 seconds.')

            match event_type:
                case 'processes':
                    stream = self.get_processes()
                case 'utilisation':
                    stream = self.get_utilisation(time_range)
                case _:
                    raise InvalidEventType()

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
        
        except (
            InvalidTimeRange,
            InvalidEventType
        ) as e:
            print(e)
            resp.status = HTTP_400
            resp.content_type = 'application/json'
            resp.text = dumps({'title': 'Bad Request', 'description': e.message})

        except Exception as e:
            self.logger.record(Metric(Label.UNEXPECTED_ERROR))
            resp.status = HTTP_500
            resp.content_type = 'application/json'
            resp.text = dumps({'title': 'Internal Server Error', 'description': 'Something went wrong!'})
            self.logger.log(Message(message=e, level=Level.ERROR, code=Code.SYSTEM))