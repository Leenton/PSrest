from configuration.Config import *
from typing import Protocol, List
from multiprocessing import Queue
from log.LogMessage import LogMessage
from enum import Enum
from time import sleep

class Logger(Protocol):
    def log(self, message: LogMessage) -> None:
        ...
    
class WindowsLogger(Logger):
    def log(message: LogMessage):
        print(str(message))

class LinuxLogger(Logger):
    def log(message: LogMessage):
        print(str(message))

class MacLogger(Logger):
    def log(message: LogMessage):
        print(str(message))

class FileLogger(Logger):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        
    def log(message: LogMessage):
        print(str(message))

class NullLogger(Logger):
    def log(message: LogMessage):
        pass

class MultiLogger(Logger):
    def __init__(self, loggers: List[Logger]):
        self.loggers = loggers
    
    def log(self, message: LogMessage):
        for logger in self.loggers:
            msg = LogMessage(message.message, message.level, message.code)
            logger.log(msg)

class PSRestLogger(Logger):
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
    
        self.logger = MultiLogger([FileLogger(self.filename),logger])

    def log(self, message: LogMessage) -> None:
        self.logger.log(message)

    def run(self, messages: Queue) -> None:
        while True:
            try:
                message: dict = messages.get(False)
                # self.log(Log)
                
            except Exception:
                sleep(0.1)

def start_logger(queue: Queue) -> None:
    try:
        logger = PSRestLogger()
        logger.run(queue)
    except KeyboardInterrupt:
        exit(0)