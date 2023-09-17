from falcon.status_codes import * 
import aiofiles

from log.LogMessage import LogMessage, LogLevel, LogCode
from log.Metric import Metric, MetricLabel
from log.MetricRecorderLogger import MetricRecorderLogger

class Home(object):
    def __init__(self, logger: MetricRecorderLogger) -> None:
        self.logger = logger

    async def on_get(self, req, resp):
        self.logger.record(Metric(MetricLabel.REQUEST))
        resp.status = HTTP_200
        resp.content_type = 'text/html'
        async with aiofiles.open('./resources/html/home.html', 'rb') as f:
            resp.text = await f.read()
        