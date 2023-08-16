from Config import * 
import json
import jwt
from exceptions.PSRExceptions import *
from entities.OAuthResponse import OAuthResponse
from OAuthToken import OAuthToken
import sqlite3
from argon2 import PasswordHasher
from uuid import uuid4
from datetime import datetime

class OAuthService():
    def __init__(self,) -> None:
        self.password_hasher = PasswordHasher()
        pass
    
    def validate_client_credential(self, client_id: str, client_secret: str) -> OAuthResponse:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(
            'SELECT cid, client_secret FROM client WHERE client_id = ?',
            (client_id,)
        )
        row = cursor.fetchone()

        if(not row):
            raise UnAuthorised('Invalid credentials.')

        if(not self.password_hasher.verify(row[1], client_secret)):
            raise UnAuthorised('Invalid credentials.')
        
        if(self.password_hasher.check_needs_rehash(row[1])):
            cursor.execute(
                'UPDATE client SET client_secret = ? WHERE cid = ?',
                (self.password_hasher.hash(client_secret), row[0])
            )
            db.commit()

        #Generate the access token 
        return OAuthResponse(
            self.get_access_token(row[0]),
            self.get_refresh_token(row[0])
        )

    def validate_refresh_token(self, refresh_token) -> OAuthResponse:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(
            'SELECT cid FROM refresh_client_map WHERE refresh_token = ? AND expiry > ?',
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

    def validate_action(self, header: str, action: str) -> None:
        #Get the access token from the header
        authorization = header.split(' ')
        if(not authorization or authorization[0].lower() != 'bearer'):
            raise UnAuthorised('Authorization scheme not supported or authorization poorly formatted.')
        
        access_token = authorization[-1]

        try:
            token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS512'])
            #Check if the action is in the list of actions for the user in the returned token
            if(token['expiry'] > datetime.timestamp(datetime.now())):
                raise InvalidToken('Access token has expired.')
            
            if action.lower() in self.get_client_actions(token['reference']):
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
                jwt.PyJWTError,
                InvalidToken) as e:
            print(e)
            raise InvalidToken('Invalid access token provided.')
    
    def validate_token(self, token: str) -> OAuthToken:
        pass

    def get_refresh_token(self, cid: int) -> str:
        #Get the refresh token associated with the cid from the db
        db = sqlite3.connect(DATABASE)

        #Delete the old refresh token
        cursor = db.cursor()
        cursor.execute(
            'DELETE FROM refresh_client_map WHERE cid = ?',
            (cid,)
        )
        db.commit()

        #Generate a new refresh token
        refresh_token = str(uuid4())
        cursor.execute(
            'INSERT INTO refresh_client_map (cid, refresh_token, expiry) VALUES (?, ?, ?)',
            (cid, refresh_token, datetime.timestamp(datetime.now()) + REFRESH_TOKEN_TTL)
        )
        db.commit()

        return refresh_token

    def get_client_actions(self, cid: str) -> list:
        #Get the actions associated with the cid from the db
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute('SELECT action FROM action_client_map WHERE cid = ?', (cid,))
        user_actions = [row[0] for row in cursor.fetchall()]

        return user_actions

    def get_access_token(self, cid: str) -> str:
        return jwt.encode(
            {
                'reference': cid, 
                'expiry': datetime.timestamp(datetime.now()) + ACCESS_TOKEN_TTL,
            },
            SECRET_KEY,
            algorithm='HS512'
        )
