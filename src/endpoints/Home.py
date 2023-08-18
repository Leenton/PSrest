from falcon.status_codes import * 
import aiofiles
from psrlogging.Logger import Logger
from psrlogging.LogMessage import LogMessage
from psrlogging.LogLevel import LogLevel
from psrlogging.LogCode import LogCode

class Home(object):
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    async def on_get(self, req, resp):
        resp.status = HTTP_200
        resp.content_type = 'text/html'
        async with aiofiles.open('./src/html/home.html', 'rb') as f:
            resp.text = await f.read()
        