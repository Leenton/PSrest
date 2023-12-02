import json
import sqlite3
from falcon.media.validators import jsonschema
from falcon.status_codes import HTTP_200, HTTP_401
from log import LogClient, Message, Level, Code
from auth import BearerTokenGenerator, BearerToken
from configuration import OAUTH_SCHEMA, CREDENTIAL_DATABASE

class OAuth(object): 
    """
    A Falcon resource class that handles OAuth authentication requests.

    Attributes:
        token_generator (BearerTokenGenerator): A generator for creating and validating bearer tokens.
        logger (LogClient): A client for logging metrics and events.
        db (sqlite3.Connection): A connection to the credential database.

    Methods:
        on_post: Handles POST requests for OAuth authentication. By validating the credentials
            provided in the request body, it returns an Bearer token if the credentials are valid.
    """
    def __init__(self, logger: LogClient) -> None:
        self.token_generator = BearerTokenGenerator()
        self.logger = logger
        self.db = sqlite3.connect(CREDENTIAL_DATABASE)
    
    @jsonschema.validate(OAUTH_SCHEMA)
    async def on_post(self, req, resp):
        resp.content_type = 'application/json'
        credentials: dict = await req.get_media()

        try:
            if(credentials['grant_type'] == 'client_credential'):
                #Check if the client id and secret are valid
                bearer_token: BearerToken = self.token_generator.validate_client_credential(
                    credentials['client_id'],
                    credentials['client_secret'])
            else:
                #Check if the refresh token is valid, if so return OAuthResponse
                bearer_token: BearerToken = self.token_generator.validate_refresh_token(
                    credentials['refresh_token'])

            resp.status = HTTP_200
            resp.text = json.dumps(bearer_token.serialise())

        except Exception:
            resp.status = HTTP_401
            resp.text = json.dumps({
                'title': 'Unauthorised',
                'description':'Invalid credentials.'
                })
