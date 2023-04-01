from uuid import uuid4
from datetime import datetime
from entities.Cmdlet import Cmdlet

class PSTicket():
    def __init__(self, command: Cmdlet) -> None:
        self.id = uuid4().hex
        self.created: int = int(datetime.timestamp(datetime.now()))
        self.expires: int = int(datetime.timestamp(datetime.now()) + float(command.ttl))
        self.ttl = command.ttl
        self.command = command.function

    def serialise(self) -> dict:
        return {
            'id': self.id,
            'created': self.created,
            'expires': self.expires,
            'ttl': self.ttl,
            'command': self.command
        }

