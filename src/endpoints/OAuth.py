import jwt

def validate(req, action):
    return True

class OAuth(): 
    def __init__(self, private_key, public_key, token_dir, encryption_key) -> None:
        pass

    def verify(self, token, action): 
        pass
    
    def add_key(self, key):
        pass

    def delete_key(self, key):
        pass

    def add_actions(self, key, actions):
        pass

    def remove_actions(self, key, actions): 
        pass
    
    async def on_post(self, req, resp):
        pass