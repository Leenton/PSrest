from typing import Protocol, List
from .Message import Message

class Logger(Protocol):
    def log(self, message: Message) -> None:
        ...
    
class WindowsLogger(Logger):
    def log(message: Message):
        print(str(message))

class LinuxLogger(Logger):
    def log(message: Message):
        print(str(message))

class MacLogger(Logger):
    def log(message: Message):
        print(str(message))

class FileLogger(Logger):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        
    def log(message: Message):
        print(str(message))

class ConsoleLogger(Logger):
    def log(message: Message):
        print(str(message))
        
class NullLogger(Logger):
    def log(message: Message):
        pass

class MultiLogger(Logger):
    def __init__(self, loggers: List[Logger]):
        self.loggers = loggers
    
    def log(self, message: Message):
        for logger in self.loggers:
            logger.log(message)
