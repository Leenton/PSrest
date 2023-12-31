from falcon.status_codes import HTTP_200
import aiofiles
from log import LogClient, Message, Level, Code
from configuration import VERSION, HELP
from json import dumps
from entities import CmdletInfoLibrary

class Home(object):
    """
    A Falcon resource class that handles GET requests for the home page.

    Attributes:
        logger (LogClient): A client for logging metrics and events.

    Methods:
        on_get: Handles GET requests for the home page.
    """
    def __init__(self, logger: LogClient, cmdlet_library: CmdletInfoLibrary) -> None:
        self.logger = logger
        self.cmdlet_library = cmdlet_library

    async def on_get(self, req, resp):
        parameters: dict = req.params

        if(bool(parameters)):
            response = {}

            if('version' in parameters):
                response['version'] = VERSION

            if('help' in parameters and HELP):
                response['help'] = self.cmdlet_library.get_cmdlets()

            resp.status = HTTP_200
            resp.content_type = 'application/json'
            resp.text = dumps(response)

        else:                    
            resp.status = HTTP_200
            resp.content_type = 'text/html'
            async with aiofiles.open('./resources/html/home.html', 'rb') as f:
                resp.text = await f.read()
            