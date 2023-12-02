import aiofiles
from falcon.status_codes import HTTP_200, HTTP_403, HTTP_404
from log import LogClient, Message, Level, Code
from configuration import DOCS
import json

class Docs(object):
    """
    A Falcon resource class that handles GET requests for the docs page.

    Attributes:
        logger (LogClient): A client for logging metrics and events.

    Methods:
        on_get: Handles GET requests for the docs page. If docs are enabled, it returns the docs page. 
    """
    def __init__(self, logger: LogClient) -> None:
        self.logger = logger

    async def on_get(self, req, resp):
        resp.content_type = 'application/json'

        if(DOCS):
            resp.status = HTTP_200
            resp.content_type = 'text/html'
            async with aiofiles.open('./resources/html/docs.html', 'rb') as f:
                resp.text = await f.read()
        else:
            resp.status = HTTP_403
            resp.text = json.dumps({'title': 'Forbidden', 'description': 'Docs are disabled on this server.'})