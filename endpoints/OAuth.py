import json
from falcon.media.validators import jsonschema
from falcon.status_codes import HTTP_200, HTTP_401
from log import LogClient, Message, Level, Code, Metric, Label
from processing import OAuthService
from configuration import OAUTH_SCHEMA
from entities import OAuthResponse

class OAuth(object): 
    def __init__(self, logger: LogClient) -> None:
        self.service = OAuthService()
        self.logger = logger
    
    @jsonschema.validate(OAUTH_SCHEMA)
    async def on_post(self, req, resp):
        self.logger.record(Metric(Label.REQUEST))
        resp.content_type = 'application/json'
        credentials: dict = await req.get_media()

        try:
            if(credentials['grant_type'] == 'client_credential'):
                #Check if the client id and secret are valid
                response_token: OAuthResponse = self.service.validate_client_credential(
                    credentials['client_id'],
                    credentials['client_secret'])
            else:
                #Check if the refresh token is valid, if so return OAuthResponse
                response_token: OAuthResponse = self.service.validate_refresh_token(
                    credentials['refresh_token'])

            resp.status = HTTP_200
            resp.text = json.dumps(response_token.serialise())

        except Exception:
            resp.status = HTTP_401
            resp.text = json.dumps({
                'title': 'Unauthorised',
                'description':'Invalid credentials.'
                })
            self.logger.record(Metric(Label.INVALID_CREDENTIALS_ERROR))