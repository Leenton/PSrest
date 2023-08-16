from falcon.status_codes import * 
import aiofiles
from Config import *
import json


class Processes(object):
    def get(self):
        return {"message": "Processes endpoint"}
    
    async def on_get(self, req, resp):
        #check if they are logged in
        #if they are serve the page else serve the login page
        resp.status = HTTP_200
        resp.content_type = 'text/html'
        async with aiofiles.open('./src/html/processes.html', 'rb') as f:
            resp.text = await f.read()

    async def on_delete(self, req, resp):
        resp.status = HTTP_200
        resp.content_type = 'application/json'
        resp.text = json.dumps({'title': 'did it!'})