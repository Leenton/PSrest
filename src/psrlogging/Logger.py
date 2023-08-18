from configuration.Config import *
from typing import Protocol, List
from queue import Queue
from psrlogging.LogMessage import LogMessage
import threading

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

class ThreadSafeLogger(Logger):
    def __init__(self, queue: Queue):
        self.message_queue = queue

    def log(self, message: LogMessage):
        with threading.Lock():
            self.message_queue.put(message)

class MultiLogger(Logger):
    def __init__(self, loggers: List[Logger]):
        self.loggers = loggers
    
    def log(self, message: LogMessage):
        for logger in self.loggers:
            msg = LogMessage(message=message.message, level=message.level, code=message.code)
            logger.log(msg)