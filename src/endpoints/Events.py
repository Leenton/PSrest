from falcon.status_codes import * 
import json
import asyncio
from falcon.asgi import SSEvent
from typing import Generator, List
from multiprocessing import Queue

from configuration.Config import *
from entities.OAuthService import OAuthService
from entities.OAuthToken import OAuthToken
from psrlogging.RecorderLogger import MetricRecorderLogger
from psrlogging.LogMessage import LogMessage
from psrlogging.Logger import LogLevel, LogCode


class Events(object):
    def __init__(self, process_events: Queue, traffic_events: Queue, logger: MetricRecorderLogger) -> None:
        self.process_events = process_events
        self.traffic_events = traffic_events
        self.oauth = OAuthService()
        self.logger = logger

    async def get_process_events(self, cid: int|str) -> Generator[List[dict], None, None]:
        while True:
            await asyncio.sleep(0.01)

            yield SSEvent(event="message", event_id=str(uuid4()), json=({'test': 2}), retry=2500)

            # try:
            #     events = self.process_events.get()
            #     filtered_events = []
            #     for event in events:            
            #         if(cid == 'admin' or cid == event['cid']):
            #             filtered_events.append(event)
                
            #     yield SSEvent(event="message", event_id=str(uuid4()), json=(filtered_events), retry=2500)
            # except Exception as e:
            #     print(e)


    async def get_traffic_events(self, cid: int) -> Generator[dict, None, None]:
        while True:
            asyncio.sleep(1)

            if(not self.process_events.empty()):
                traffic_events = self.traffic_events[0]

                yield SSEvent(event="message", event_id=str(uuid4()), json=(traffic_events), retry=5000)


    async def on_get(self, req, resp, event_type: str = ''):
        token: OAuthToken = self.oauth.validate_token(req.get_header('Authorization') or '')

        if event_type.lower() in ['processes', 'traffic']:
            resp.status = HTTP_200
            resp.content_type = 'text/event-stream'
            resp.sse = self.get_process_events('admin') if event_type.lower() == 'processes' else self.get_traffic_events()

        elif event_type.lower() == 'static':
            resp.status = HTTP_200
            resp.content_type = 'application/json'

            if(not self.process_events.empty()):
                events = self.process_events[0]
                filtered_events = []

                for event in events:            
                    if(token.user == 'admin' or token.user == event['cid']):
                        filtered_events.append(event)
                        
                resp.text = json.dumps(filtered_events)

        else:
            resp.status = HTTP_404
            resp.content_type = 'application/json'
            resp.text = json.dumps({'title': '404 Not Found', 'description': 'The page you are looking for does not exist.'})