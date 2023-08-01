from Config import * 
import json
import jwt
from exceptions.PSRExceptions import *
from entities.OAuthResponse import OAuthResponse

class OAuthService():
    def __init__(self,) -> None:
        pass
    
    def validate_client_credential(self, client_id, client_secret) -> OAuthResponse:
        #check if the client id is in the db
        #check if the client secret is in the db
        json.dumps({'title': 'Unauthorized', 'description': 'Invalid credentials.'})
        pass

    def validate_refresh_token(self, refresh_token) -> OAuthResponse:
        #check if the refresh token is in the db
        pass

    def validate_action(access_token: str, action: str) -> None:
        try:
            token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS512'])
            #check if the action is in the list of actions for the user in the returned token
            if action in token['array']:
                return
            else:
                raise UnAuthorised('You do not have permission to perform this action.')
        except (jwt.DecodeError,
                jwt.ExpiredSignatureError,
                jwt.ImmatureSignatureError,
                jwt.InvalidAlgorithmError,
                jwt.InvalidAudienceError,
                jwt.InvalidIssuedAtError,
                jwt.InvalidIssuerError,
                jwt.InvalidKeyError,
                jwt.InvalidSignatureError,
                jwt.InvalidTokenError,
                jwt.MissingRequiredClaimError,
                jwt.PyJWKClientError,
                jwt.PyJWKError,
                jwt.PyJWKSetError,
                jwt.PyJWTError):
            
            raise InvalidToken('Invalid access token provided.')

    def get_access_token(self, client_id: str) -> str:
        return jwt.encode({'client_id': client_id, 'array':[]}, SECRET_KEY, algorithm='HS512')