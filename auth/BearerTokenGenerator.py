from jwt import encode
from argon2 import PasswordHasher
from datetime import datetime
from uuid import uuid4
from sqlite3 import connect
from configuration import CREDENTIAL_DATABASE, SECRET_KEY, ACCESS_TOKEN_TTL, REFRESH_TOKEN_TTL
from errors import InvalidCredentials

class BearerToken():
    def __init__(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.expires_in = ACCESS_TOKEN_TTL
        self.refresh_token = refresh_token

    def serialise(self):
        return {
            'access_token': self.access_token,
            'expires_in': self.expires_in,
            'refresh_token': self.refresh_token
        }

class BearerTokenGenerator():
    def __init__(self,) -> None:
        self.password_hasher = PasswordHasher()
        self.db = connect(CREDENTIAL_DATABASE)
    
    def validate_client_credential(self, client_id: str, client_secret: str) -> BearerToken:
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT cid, client_secret FROM client WHERE client_id = ?",
            (client_id,)
        )
        row = cursor.fetchone()

        if(not row):
            raise InvalidCredentials('Invalid credentials.')

        if(not self.password_hasher.verify(row[1], client_secret)):
            raise InvalidCredentials('Invalid credentials.')
        
        if(self.password_hasher.check_needs_rehash(row[1])):
            cursor.execute(
                "UPDATE client SET client_secret = ? WHERE cid = ?",
                (self.password_hasher.hash(client_secret), row[0])
            )
            self.db.commit()

        #Generate the access token 
        return BearerToken(
            self.get_access_token(row[0]),
            self.get_refresh_token(row[0])
        )

    def validate_refresh_token(self, refresh_token) -> BearerToken:

        cursor = self.db.cursor()
        cursor.execute(
            "SELECT cid FROM refresh_client_map WHERE refresh_token = ? AND expiry > ?",
            (refresh_token, datetime.timestamp(datetime.now()))
        )
        row = cursor.fetchone()
        
        if(not row):
            raise InvalidCredentials('Invalid credentials.')

        #Generate the access token
        return BearerToken(
            self.get_access_token(row[0]),
            self.get_refresh_token(row[0])
        )

    def get_refresh_token(self, cid: int) -> str:
        #Delete the old refresh token
        cursor = self.db.cursor()
        cursor.execute(
            "DELETE FROM refresh_client_map WHERE cid = ?",
            (cid,)
        )
        self.db.commit()

        #Generate a new refresh token
        refresh_token = str(uuid4())
        cursor.execute(
            "INSERT INTO refresh_client_map (cid, refresh_token, expiry) VALUES (?, ?, ?)",
            (cid, refresh_token, datetime.timestamp(datetime.now()) + REFRESH_TOKEN_TTL)
        )
        self.db.commit()

        return refresh_token

    def get_access_token(self, cid: str) -> str:
        return encode(
            {
                'reference': cid, 
                'expiry': datetime.timestamp(datetime.now()) + ACCESS_TOKEN_TTL,
            },
            SECRET_KEY,
            algorithm='HS512'
        )