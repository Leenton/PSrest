class PSResponseStorage():
    def __init__(self) -> None:
        self.responses = {}
    
    def store(self, ticket, response):
        self.responses[ticket] = response
    
    def get(self, ticket):
        return self.responses[ticket]
    
    def delete(self, ticket):
        del self.responses[ticket]
    
    def get_all(self):
        return self.responses