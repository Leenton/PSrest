from falcon.status_codes import * 
import aiofiles
from log import LogClient, Message, Level, Code, Metric, Label
class Home(object):
    def __init__(self, logger: LogClient) -> None:
        self.logger = logger

    async def on_get(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))
        resp.status = HTTP_200
        resp.content_type = 'text/html'
        async with aiofiles.open('./resources/html/home.html', 'rb') as f:
            resp.text = await f.read()
        