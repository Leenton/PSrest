from psrlogging.Logger import LogLevel, LogCode
from datetime import datetime

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
