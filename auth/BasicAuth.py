from base64 import b64decode
from sqlite3 import connect
from argon2 import PasswordHasher
from configuration import CREDENTIAL_DATABASE
from errors import InvalidCredentials
from errors import InvalidCredentials
from .AuthorisationToken import AuthorisationToken

class BasicAuth():
    def __init__(self):
        self.user = 'admin'
        self.password = 'admin'
        self.db = connect(CREDENTIAL_DATABASE)
        self.password_hasher = PasswordHasher()


    def authenticate(self, token: AuthorisationToken) -> None:
        try:
            t = b64decode(token.value.encode('utf-8')).decode('utf-8')
            user, password = t.split(':')
            
            # check if the user is in the database
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT hash,role, uid, name FROM user WHERE name LIKE ?",
                (user.lower(),)
            )
            row = cursor.fetchone()
            if(not row):
                raise InvalidCredentials('Either the user does not exist, or the password is incorrect.')
            
            if(not self.password_hasher.verify(row[0], password)):
                raise InvalidCredentials('Either the user does not exist, or the password is incorrect.')
            
            if(self.password_hasher.check_needs_rehash(row[0])):
                cursor.execute(
                    "UPDATE user SET hash = ? WHERE uid = ?",
                    (self.password_hasher.hash(password), row[2])
                )
                self.db.commit()

            token.reference = row[2]
            token.role = row[1]
            token.user = user[3]
            cursor.close()

        except:
            raise InvalidCredentials('Unable to authenticate.')

    def get_allowed_actions(self, role:str) -> list[str]:
        if role == 'admin':
            return ['kill', 'view']
        elif role == 'user':
            return ['view']