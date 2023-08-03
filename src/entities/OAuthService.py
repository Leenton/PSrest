from Config import * 
import json
import jwt
from exceptions.PSRExceptions import *
from entities.OAuthResponse import OAuthResponse
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

    def validate_action(access_token: str, action: str) -> None:
        try:
            token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS512'])
            #check if the action is in the list of actions for the user in the returned token
            if action in token['action'] and token['expiry'] > datetime.timestamp(datetime.now()):
                #Log the action and the client id somewhere
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
    
    def get_refresh_token(self, cid: int) -> str:
        #Get the refresh token associated with the c                                                                                                                                 id from the db
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
        actions = cursor.fetchall()
        
        user_actions = []
        for action in actions:
            user_actions.append(action[0])

        return user_actions


    def get_access_token(self, cid: str) -> str:
        return jwt.encode(
            {
                'reference': cid, 
                'actions':self.get_client_actions(cid),
                'expiry': datetime.timestamp(datetime.now()) + ACCESS_TOKEN_TTL
            },
            SECRET_KEY,
            algorithm='HS512'
        )
