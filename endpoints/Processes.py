from falcon.status_codes import * 
import aiofiles
from configuration.Config import *
import json
from log import LogClient, Message, Level, Code, Metric, Label

class Processes(object):
    def __init__(self, logger: LogClient) -> None:
        self.logger = logger

    def get(self):
        return {"message": "Processes endpoint"}
    
    async def on_get(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))
        #check if they are logged in
        #if they are serve the page else serve the login page
        resp.status = HTTP_200
        resp.content_type = 'text/html'
        async with aiofiles.open('./resources/html/processes.html', 'rb') as f:
            resp.text = await f.read()

    async def on_delete(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))
        resp.status = HTTP_200
        resp.content_type = 'application/json'
        resp.text = json.dumps({'title': 'did it!'})