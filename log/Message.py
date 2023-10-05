from enum import Enum
from datetime import datetime

class Code(Enum):
    GENERIC = 1
    SYSTEM = 2

class Level(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class Message():
    def __init__(
            self,
            message: str,
            level: Level | str = Level.INFO,
            code: Code | str = Code.SYSTEM,
            timestamp: float = datetime.timestamp(datetime.now())
        ) -> None:
        if not isinstance(level, Level):
            try:
                level = Level[level]
            except KeyError:
                raise ValueError(f'Level {level} is not a valid level')

        if not isinstance(code, Code):
            try:
                code = Code[code]
            except KeyError:
                raise ValueError(f'Code {code} is not a valid code')
            
        self.message: str = message
        self.timestamp: float = timestamp
        self.level: Level = level
        self.code: Code = code
    
    def serialise(self) -> dict:
        return {
            'message': self.message,
            'level': self.level.name,
            'code': self.code.name,
            'timestamp': self.timestamp
        }

