from enum import Enum
from datetime import datetime

class LogCode(Enum):
    GENERIC = 1
    SYSTEM = 2

class LogLevel(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class LogMessage():
    def __init__(self, message: str, level: LogLevel = LogLevel.INFO, code: LogCode = LogCode.SYSTEM):
        self.message = message
        self.timestamp = datetime.now()
        self.level = level
        self.code = code
    
    def serialise(self) -> dict:
        return {
            'message': self.message,
            'timestamp': self.timestamp,
            'level': self.level.name,
            'code': self.code.name
        }
    
    def __str__(self) -> str:
        return f'[{self.timestamp}] [{self.level.name}] [{self.code.name}] {self.message}'

