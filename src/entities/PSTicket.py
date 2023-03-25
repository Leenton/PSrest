from uuid import uuid4
from datetime import datetime

class PSTicket():
    def __init__(self, ttl) -> None:
        self.id = uuid4().hex
        self.created: int = int(datetime.timestamp(datetime.now()))
        self.expires: int = int(datetime.timestamp(datetime.now()) + ttl)

    def serialise(self):
        return {
            'id': self.id,
            'created': self.created,
            'expires': self.expires
        }

