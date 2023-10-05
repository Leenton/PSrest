from falcon.status_codes import HTTP_200, HTTP_404
from json import loads, dumps
from asyncio import sleep
from falcon.asgi import SSEvent
from typing import Generator, List
from uuid import uuid4
from datetime import datetime
from log import LogClient, Message, Level, Code, Metric, Label
from entities import ProcessorConnection, OAuthToken
from processing import ResourceMonitor, OAuthService

class Events(object):
    def __init__(self, logger: LogClient) -> None:
        self.oauth = OAuthService()
        self.logger = logger
        self.resource_monitor = ResourceMonitor()

    async def get_processes(self,) -> Generator[List[dict], None, None]:
        while True:
            await sleep(0.25)
            reader, writer = await (ProcessorConnection()).connect()
            writer.write(b'p')
            await writer.drain()
            snapshot = loads((await reader.read()).decode('utf-8'))
            writer.close()

            yield SSEvent(event="message", event_id=str(uuid4()), json=(snapshot), retry=2500)

    async def get_usage(self, time_range: int = 300) -> Generator[dict, None, None]:
        while True:
            await sleep(1)
            start = int(datetime.timestamp(datetime.now()))
            end = start - time_range
            metrics = await self.resource_monitor.get_usage(start, end)

            yield SSEvent(event="message", event_id=str(uuid4()), json=(metrics), retry=5000)

    async def on_get(self, req, resp, event_type: str = ''):
        self.logger.record(Metric(Label.REQUEST))
        token: OAuthToken = self.oauth.validate_token(req.get_header('Authorization') or '')

        match event_type:
            case 'processes':
                resp.status = HTTP_200
                resp.content_type = 'text/event-stream'
                resp.sse = self.get_processes()
            case 'usage':
                resp.status = HTTP_200
                resp.content_type = 'text/event-stream'
                resp.sse = self.get_usage()
            case 'static':
                resp.status = HTTP_200
                resp.content_type = 'application/json'
                resp.text = dumps({'title': 'did it!'})
            case _:
                resp.status = HTTP_404
                resp.content_type = 'application/json'
                resp.text = dumps({'title': '404 Not Found', 'description': 'The event type you are looking for does not exist.'})