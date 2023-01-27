from uuid import uuid4
from datetime import datetime

class PSTicket():
    def __init__(self, ttl) -> None:
        self.id = uuid4()
        self.created = datetime.timestamp(datetime.now())
        self.expires = datetime.timestamp(datetime.now()) + ttl
