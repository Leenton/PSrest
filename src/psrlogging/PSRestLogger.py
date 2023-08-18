from configuration.Config import *
from psrlogging.Logger import *
from psrlogging.LogMessage import LogMessage
from queue import Queue
from time import sleep

class PSRestLogger(Logger):
    def __init__(self) -> None:
        self.log_level = LOG_LEVEL
        self.filename = LOG_FILE

        if LOG_PLATFORM == 'Windows':
            logger = WindowsLogger()
        elif LOG_PLATFORM== 'Linux':
            logger = LinuxLogger()
        elif LOG_PLATFORM == 'MacOS':
            logger = MacLogger()
        else:
            logger = NullLogger()
    
        self.logger = MultiLogger([
            FileLogger(self.filename),logger])

    def log(self, message: LogMessage) -> None:
        self.logger.log(message)

    def run(self, messages: Queue) -> None:
        while True:
            try:
                message: LogMessage = messages.get()
                self.log(message)
            except Exception:
                sleep(0.1)

def start_logger(queue: Queue) -> None:
    logger = PSRestLogger()
    logger.run(queue)
