import aiofiles
from falcon.status_codes import HTTP_200, HTTP_403, HTTP_404
from log import LogClient, Message, Level, Code
from configuration import DOCS, RESOURCE_DIR
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
        self.doc_pages = ['index', 'oauth', 'run', 'config', 'resources']

    async def on_get(self, req, resp, page=None):
        resp.content_type = 'application/json'

        if(not DOCS):
            resp.status = HTTP_404
            resp.text = json.dumps({'title': 'Not Found', 'description': 'Docs are disabled on this server.'})

        elif(page == None):
            resp.status = HTTP_200
            resp.content_type = 'text/html'
            async with aiofiles.open(RESOURCE_DIR + '/html/docs.html', 'rb') as f:
                resp.text = await f.read()

        elif(str(page).lower() in self.doc_pages):
            resp.status = HTTP_200
            resp.content_type = 'text/html'
            async with aiofiles.open( RESOURCE_DIR + f'/html/docs/{page}.html', 'rb') as f:
                resp.text = await f.read()

        else:
            resp.status = HTTP_404
            resp.text = json.dumps({'title': 'Not Found', 'description': 'The requested page was not found.'})
