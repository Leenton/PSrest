from uuid import uuid4
from datetime import datetime
from entities.Cmdlet import Cmdlet

class Ticket():
    def __init__(self, command: dict) -> None:
        self.id = uuid4().hex
        self.created: float = datetime.timestamp(datetime.now())
        self.expires: float = datetime.timestamp(datetime.now()) + float(command['ttl'])
        self.ttl: float = command['ttl']
        self.command: dict = command
        self.pid: str = ''

    def serialise(self) -> dict:
        return {
            'id': self.id,
            'created': self.created,
            'expiry': self.expires,
            'ttl': self.ttl,
            'command': self.command,
            'pid': self.pid
        }

