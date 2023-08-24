from falcon.status_codes import * 
import aiofiles
import os
import json

from configuration.Config import *
from psrlogging.LogMessage import LogMessage, LogLevel, LogCode
from psrlogging.Metric import Metric, MetricLabel
from psrlogging.MetricRecorderLogger import MetricRecorderLogger

class Resources(object):
    def __init__(self, logger: MetricRecorderLogger) -> None:
        self.logger = logger

    async def on_get(self, req, resp, resource):
        self.logger.record(Metric(MetricLabel.REQUEST))
        #check if the file exists
        if not os.path.isfile(RESOURCE_DIR + '/' + resource):
            resp.status = HTTP_404
            resp.content_type = 'application/json'
            resp.text = json.dumps({'title': '404 Not Found', 'description': 'The page you are looking for does not exist.'})
        else:
            #logic to check what the file extension is and to set the correct header based on the file type. 
            file_format = (resource.split('.'))[-1]
            match (file_format):
                case 'css':
                    resp.content_type = 'text/css'
                case 'htm':
                    resp.content_type = 'text/html'
                case 'html':
                    resp.content_type = 'text/html'
                case 'jpg':
                    resp.content_type = 'image/jpg'
                case 'png':
                    resp.content_type = 'image/png'
                case 'svg':
                    resp.content_type = 'image/svg+xml'
                case 'gif':
                    resp.content_type = 'image/gif'
                case 'ttf':
                    resp.content_type = 'image/ttf'
                case 'js':
                    resp.content_type = 'text/javascript'
                case other :
                    resp.status = HTTP_404
                    resp.content_type = 'application/json'
                    resp.text = json.dumps({'title': '404 Not Found', 'description': 'The page you are looking for does not exist.'})
            
            resp.status = HTTP_200
            async with aiofiles.open(RESOURCE_DIR + '/' + resource , 'rb') as f:
                resp.text = await f.read()
