class OAuthToken(object):
    def __init__(self, token: str, expires_in: int, refresh_token: str) -> None:
        self.token = token
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.user = 0
    
