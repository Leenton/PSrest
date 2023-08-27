# import python dependencies and 3rd party modules
import json
from falcon.media.validators import jsonschema
from falcon.status_codes import HTTP_200, HTTP_401

# import project dependencies
from exceptions.PSRExceptions import *
from entities.OAuthResponse import OAuthResponse
from entities.OAuthService import OAuthService
from entities.Schema import OAUTH_SCHEMA
from psrlogging.LogMessage import LogMessage, LogLevel, LogCode
from psrlogging.Metric import Metric, MetricLabel
from psrlogging.MetricRecorderLogger import MetricRecorderLogger
from configuration.Config import * 

class OAuth(object): 
    def __init__(self, logger: MetricRecorderLogger) -> None:
        self.service = OAuthService()
        self.logger = logger
    
    @jsonschema.validate(OAUTH_SCHEMA)
    async def on_post(self, req, resp):
        self.logger.record(Metric(MetricLabel.REQUEST))
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

        except Exception as e:
            resp.status = HTTP_401
            resp.text = json.dumps({
                'title': 'Unauthorised',
                'description':'Invalid credentials.'
                })
            self.logger.record(Metric(MetricLabel.INVALID_CREDENTIALS_ERROR))