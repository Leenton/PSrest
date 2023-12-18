from uuid import uuid4
from datetime import datetime

class Ticket():
    def __init__(self, command: dict) -> None:
        self.id = uuid4().hex
        self.created: float = datetime.timestamp(datetime.now())
        self.expiry: float = datetime.timestamp(datetime.now()) + float(command['ttl'])
        self.ttl: float = command['ttl']
        self.command: dict = command
        self.pid: str = ''

    def serialise(self) -> dict:
        return {
            'id': self.id,
            'created': self.created,
            'expiry': self.expiry,
            'ttl': self.ttl,
            'fucntion: ': self.command['function'],
            'application_name': self.command['application_name'],
            'pid': self.pid
        }
