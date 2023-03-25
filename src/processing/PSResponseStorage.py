from datetime import datetime
from entities.PSTicket import PSTicket
class PSResponseStorage():
    def __init__(self) -> None:
        self.responses = {}
    
    def store(self, ticket: PSTicket, response):
        self.responses[ticket.id] = response
    
    async def get(self, ticket: PSTicket):
        while(ticket.expires > int(datetime.timestamp(datetime.now()))):
            if(ticket in self.responses):
                return self.responses[ticket.id]
        raise Exception('Ticket expired before response was received')
    
    def delete(self, ticket: PSTicket):
        del self.responses[ticket.id]
    
    def get_all(self):
        return self.responses