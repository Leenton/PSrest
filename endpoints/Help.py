import aiofiles
from falcon.status_codes import HTTP_200, HTTP_403, HTTP_404
import json 
from html import escape
from log import LogClient, Message, Level, Code, Metric, Label
from entities import CmdletInfo, CmdletInfoLibrary
from configuration import HELP

class Help(object):
    """
    A Falcon resource class that handles GET requests for the help page.

    Attributes:
        cmdlet_library (CmdletInfoLibrary): A library of cmdlet information.
        logger (LogClient): A client for logging metrics and events.

    Methods:
        on_get: Handles GET requests for the help page. If a cmdlet is specified in the URL, it
            builds a help page for that cmdlet. Otherwise, it returns the default help page.
        build_help_page: Builds an HTML help page for a given cmdlet.
    """
    def __init__(self, logger: LogClient) -> None:
        self.cmdlet_library = CmdletInfoLibrary()
        self.logger = logger

    async def on_get(self, req, resp, command: str | None = None):
        self.logger.record(Metric(Label.REQUEST))
        resp.content_type = 'application/json'

        if(not HELP):
                #Replace this with the fancy 500 error page
                resp.status = HTTP_403
                resp.text = json.dumps({'title': 'Forbidden', 'description': 'Help is disabled on this server.'})

        elif command and (info := self.cmdlet_library.get_cmdlet(command.lower())):
                resp.status = HTTP_200
                resp.content_type = 'text/html'
                resp.text = self.build_help_page(info)

        elif command:
                resp.status = HTTP_404
                resp.text = json.dumps({'title': '404 Not Found', 'description': 'The page you are looking for does not exist.'})
                
        else:
            resp.status = HTTP_200
            resp.content_type = 'text/html'
            async with aiofiles.open('./resources/html/help.html', 'rb') as f:
                resp.text = await f.read()

    def build_help_page(self, info: CmdletInfo) -> str:
        indents, content = self.get_style_and_content(info.help)
        
        return """<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Help - """ + escape(info.command) + """</title>
                <style>
                    body {
                        margin: auto;
                        max-width: 75%;
                        font-family: monospace;
                    }
                    .indent0 {
                        margin-left: 0px;
                        font-weight: bold;
                        font-size: large;
                    }
                    """ + "".join(indents) + """
                </style>
            </head>
            <body>""" + "".join(content) + """
            </body>
            </html>"""
    
    def get_style_and_content(self, help: str):
        indents = []
        content = []
        style = []
        lines = help.splitlines()

        for line in lines:
            #count number of spaces at the start of the line
            indent = 0
            for char in line:
                if(char == ' '):
                    indent += 1
                else:
                    break
            if(indent not in indents and indent != 0):
                indents.append(indent)
            content.append(f"<p class=\"indent{indent}\">" + escape(line.strip()) + "</p>\n")

        for indent in indents:
            style.append(""".indent""" + str(indent) + """ {
                        margin-left: """ + str(indent) + """em;
                        }\n""")   
            
        return (style, content)