from PSProcessor import PSProcessor
from RestParser import *
from PSParser import *
from entities.Cmdlet import Cmdlet
#endpoint that gets called to actually execute the commands we want to execute with our application.

class Run(object):
    def __init__(self) -> None:
        self.processor = PSProcessor()
        
    async def run(self, command: Cmdlet):
        self.processor.execute(command)
        result = self.processor.recieve(command)
        return serialize(result)
        
    async def on_get(self, req, resp, command):
        try:
            result = self.run(parse(command))
        except: 
            pass
    
    async def on_post(self, req, resp, command):
        try:
            result = self.run(parse(command))
        except: 
            pass

    async def on_put(self, req, resp, command):
        try:
            result = self.run(parse(command))
        except: 
            pass

    async def on_delete(self, req, resp, command):
        try:
            result = self.run(parse(command))
        except: 
            pass
