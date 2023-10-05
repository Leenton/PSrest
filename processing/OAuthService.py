import sqlite3
from argon2 import PasswordHasher
from uuid import uuid4
from datetime import datetime
from jwt import (
    DecodeError,
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidIssuedAtError,
    InvalidIssuerError,
    InvalidKeyError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
    PyJWKClientError,
    PyJWKError,
    PyJWKSetError,
    decode,
    encode
)
from configuration import (
    CREDENTIAL_DATABASE,
    SECRET_KEY,
    ACCESS_TOKEN_TTL,
    REFRESH_TOKEN_TTL,
    ARBITRARY_COMMANDS
)
from entities import OAuthToken, OAuthResponse
from errors import UnAuthorised, InvalidToken 

class OAuthService():
    def __init__(self,) -> None:
        self.password_hasher = PasswordHasher()
        self.db = sqlite3.connect(CREDENTIAL_DATABASE)
    
    def validate_client_credential(self, client_id: str, client_secret: str) -> OAuthResponse:
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT cid, client_secret FROM client WHERE client_id = ?",
            (client_id,)
        )
        row = cursor.fetchone()

        if(not row):
            raise UnAuthorised('Invalid credentials.')

        if(not self.password_hasher.verify(row[1], client_secret)):
            raise UnAuthorised('Invalid credentials.')
        
        if(self.password_hasher.check_needs_rehash(row[1])):
            cursor.execute(
                "UPDATE client SET client_secret = ? WHERE cid = ?",
                (self.password_hasher.hash(client_secret), row[0])
            )
            self.db.commit()

        #Generate the access token 
        return OAuthResponse(
            self.get_access_token(row[0]),
            self.get_refresh_token(row[0])
        )

    def validate_refresh_token(self, refresh_token) -> OAuthResponse:

        cursor = self.db.cursor()
        cursor.execute(
            "SELECT cid FROM refresh_client_map WHERE refresh_token = ? AND expiry > ?",
            (refresh_token, datetime.timestamp(datetime.now()))
        )
        row = cursor.fetchone()
        
        if(not row):
            raise UnAuthorised('Invalid credentials.')

        #Generate the access token
        return OAuthResponse(
            self.get_access_token(row[0]),
            self.get_refresh_token(row[0])
        )

    def get_authorized_application_name(self, header: str, action: str) -> str:
        #Get the access token from the header
        authorisation = header.split(' ')
        if(not authorisation or authorisation[0].lower() != 'bearer'):
            raise UnAuthorised('Authorisation scheme not supported or authorisation poorly formatted.')
        
        access_token = authorisation[-1]

        try:
            token = decode(access_token, SECRET_KEY, algorithms=['HS512'])
            #Check if the action is in the list of actions for the user in the returned token
            if(token['expiry'] > datetime.timestamp(datetime.now())):
                raise InvalidToken('Access token has expired.')
            
            if ARBITRARY_COMMANDS or action.lower() in self.get_client_actions(token['reference']):
                return self.get_client_name(token['reference'])
            
            else:
                raise UnAuthorised('You do not have permission to perform this action.')
            
        except (
            DecodeError,
            ExpiredSignatureError,
            ImmatureSignatureError,
            InvalidAlgorithmError,
            InvalidAudienceError,
            InvalidIssuedAtError,
            InvalidIssuerError,
            InvalidKeyError,
            InvalidSignatureError,
            InvalidTokenError,
            MissingRequiredClaimError,
            PyJWKClientError,
            PyJWKError,
            PyJWKSetError,
            InvalidToken
        ) as e:
            print(e)
            raise InvalidToken('Invalid access token provided.')
    
    def validate_token(self, token: str) -> OAuthToken:
        pass

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

    def get_client_actions(self, cid: str) -> list:
        #Get the actions associated with the cid from the db
        cursor = self.db.cursor()
        cursor.execute("SELECT action FROM action_client_map WHERE cid = ?", (cid,))
        user_actions = [row[0] for row in cursor.fetchall()]

        return user_actions
    
    def get_client_name(self, cid: str) -> str:
        cursor = self.db.cursor()
        cursor.execute("SELECT name FROM client WHERE cid = ?", (cid,))
        name = cursor.fetchone()[0]

        return name

    def get_access_token(self, cid: str) -> str:
        return encode(
            {
                'reference': cid, 
                'expiry': datetime.timestamp(datetime.now()) + ACCESS_TOKEN_TTL,
            },
            SECRET_KEY,
            algorithm='HS512'
        )
