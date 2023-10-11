from falcon.status_codes import HTTP_200
import aiofiles
from log import LogClient, Message, Level, Code, Metric, Label

class Home(object):
    """
    A Falcon resource class that handles GET requests for the home page.

    Attributes:
        logger (LogClient): A client for logging metrics and events.

    Methods:
        on_get: Handles GET requests for the home page.
    """
    def __init__(self, logger: LogClient) -> None:
        self.logger = logger

    async def on_get(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))
        resp.status = HTTP_200
        resp.content_type = 'text/html'
        async with aiofiles.open('./resources/html/home.html', 'rb') as f:
            resp.text = await f.read()
        