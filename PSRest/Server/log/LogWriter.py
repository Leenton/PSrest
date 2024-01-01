from configuration import LOG_FILE, PLATFORM
from .Logger import * 
from .Message import *

class LogWriter():
    def __init__(self) -> None:
        self.filename = LOG_FILE

        if PLATFORM == 'Windows':
            logger = WindowsLogger()

        elif PLATFORM== 'Linux':
            logger = LinuxLogger()

        elif PLATFORM == 'MacOS':
            logger = MacLogger()

        else:
            logger = NullLogger()
    
        self.logger = MultiLogger([FileLogger(self.filename), ConsoleLogger(), logger])

    def write(self, message: dict) -> None:
        message = Message(**message)
        self.logger.log(message)