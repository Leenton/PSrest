from configuration.Config import *

class OAuthResponse():
    def __init__(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.expires_in = ACCESS_TOKEN_TTL
        self.refresh_token = refresh_token

    def serialise(self):
        return {
            'AccessToken': self.access_token,
            'ExpiresIn': self.expires_in,
            'RefreshToken': self.refresh_token
        }