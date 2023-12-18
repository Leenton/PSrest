from datetime import datetime
from sqlite3 import connect
from configuration import CREDENTIAL_DATABASE, SECRET_KEY
from .AuthorisationToken import AuthorisationToken
from errors import UnAuthorised, InvalidToken
from jwt import decode

class BearerAuth():
    def __init__(self):
        self.db = connect(CREDENTIAL_DATABASE)

    def authenticate(self, token: AuthorisationToken):
        try:
            bearer_token = decode(token.value, SECRET_KEY, algorithms=['HS512'])
            #Check if the action is in the list of actions for the user in the returned token
            if(bearer_token['expiry'] > datetime.timestamp(datetime.now())):
                raise InvalidToken('Access token has expired.')
            
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT name FROM client WHERE cid = ?",
                (bearer_token['reference'],)
            )
            row = cursor.fetchone()
            if(not row):
                raise UnAuthorised('Couldn\'t identify the user associated with this token.')
            token.user = row[0]
            token.value = bearer_token
            cursor.close()
            
        except Exception:
            raise InvalidToken('Invalid access token provided.')
        
    def get_allowed_actions(self, reference: str) -> list[str]:
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT action FROM client_action WHERE cid = ?",
                (reference,)
            )
            row = cursor.fetchall()
            cursor.close()
            return [action[0] for action in row]
        
        except Exception:
            raise UnAuthorised('Unable to verify permissions.')        

