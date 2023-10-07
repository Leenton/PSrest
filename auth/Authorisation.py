from errors import UnAuthorised, InvalidToken 
from .BasicAuth import BasicAuth
from .BearerAuth import BearerAuth
from .AuthorisationToken import AuthorisationToken, AuthorisationSchema
from configuration import ARBITRARY_COMMANDS

class Authorisation():
    def __init__(self):
        self.basic_auth_service = BasicAuth()
        self.bearer_auth_service = BearerAuth()
        self.admin_actions = ['kill', 'view']

    def get_token(self, req) -> AuthorisationToken:
        token = req.get_header('Authorization')

        if not isinstance(token, str):
            raise InvalidToken('Authorisation header must be a string.')
        
        schema = token.split(' ', 1)[0].lower()
        if(type == AuthorisationSchema.BASIC.value.lower()):
            schema =  AuthorisationSchema.BASIC
        elif(type == AuthorisationSchema.BEARER.value.lower()):
            schema = AuthorisationSchema.BEARER
        else:
            raise InvalidToken('Authorisation scheme not supported.')
        
        return AuthorisationToken(schema, token.split(' ', 1).pop())


    def is_authorised(self, token: AuthorisationToken, action: str, schema: AuthorisationSchema) -> bool:
        if(token.schema != schema):
            raise UnAuthorised(f'{token.schema.value} authentication is not supported for this action. Please use {schema.value} authentication with an access token.')

        # associate the token with a user
        match token.schema:
            case AuthorisationSchema.BASIC:
                self.basic_auth_service.authenticate(token)
            case AuthorisationSchema.BEARER:
                self.bearer_auth_service.authenticate(token)

        # check if the user has permission to do the action
        if schema == AuthorisationSchema.BASIC  and action in self.basic_auth_service.get_allowed_actions(token.role) :
            return True
        
        if schema == AuthorisationSchema.BEARER and (action in self.bearer_auth_service.get_allowed_actions(token.reference) or ARBITRARY_COMMANDS):
            return True
        
        raise UnAuthorised(f'Insufficient permissions to perform this action.')