from uuid import uuid4
from datetime import datetime
from entities.Cmdlet import Cmdlet

class PSTicket():
    def __init__(self, command: Cmdlet) -> None:
        self.id = uuid4().hex
        self.created: float = datetime.timestamp(datetime.now())
        self.expires: float = datetime.timestamp(datetime.now()) + float(command.ttl)
        self.ttl: float = command.ttl
        self.command: str = command.function
        self.application_name: str = ''

    def serialise(self) -> dict:
        return {
            'id': self.id,
            'created': self.created,
            'expires': self.expires,
            'ttl': self.ttl,
            'command': self.command,
            'application_name': self.application_name
        }

