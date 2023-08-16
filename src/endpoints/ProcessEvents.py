from falcon.status_codes import * 
import aiofiles
import os
from Config import *
import json
import asyncio
from falcon.asgi import SSEvent
from entities.OAuthService import OAuthService
from entities.OAuthToken import OAuthToken
from typing import Generator, List
from queue import Queue

class ProcessEvents(object):
    def __init__(self, process_events: Queue, traffic_events: Queue) -> None:
        self.process_events = process_events
        self.traffic_events = traffic_events
        self.oauth = OAuthService()

    async def get_process_events(self, cid: int) -> Generator[List[dict]]:
        while True:
            asyncio.sleep(0.01)

            if(not self.process_events.empty()):
                events = self.process_events[0]
                filtered_events = []
                for event in events:            
                    if(cid == 'admin' or cid == event['cid']):
                        filtered_events.append(event)
                
                yield SSEvent(event="message", event_id=str(uuid4()), json=(filtered_events), retry=2500)


    async def get_traffic_events(self, cid: int) -> Generator[list]:
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
            resp.sse = self.get_process_events(token.user) if event_type.lower() == 'processes' else self.get_traffic_events()

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