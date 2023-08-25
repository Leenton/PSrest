import sqlite3
from configuration.Config import * 
import jwt
from argon2 import PasswordHasher
import sqlite3
from datetime import datetime, timedelta
from typing import List

class PSRestConsole():
    def __init__(self,) -> None:
        self.service = 1
        self.database = sqlite3.connect(CREDENTIAL_DATABASE)

    def run(self, request: dict) -> dict:
        if request['method'] == 'add':

            return self.add_application(
                request['name'],
                request['description'],
                request['authentication'],
                request['actions']
            )
        
        elif request['method'] == 'remove':
            return self.remove_application(request['id'])
        
        elif request['method'] == 'get':
            if 'name' in request:
                return self.get_application(name=request['name'])
            
            elif 'id' in request:
                return self.get_application(id=request['id'])
            
            else:
                return self.get_application()
            
        elif request['method'] == 'set':

            return self.set_application(
                request['id'],
                request.get('description', None),
                request.get('actions', None),
            )
    
    def get_application(self, name: str|None = None, id: int|None = None) -> dict:
        cursor = self.database.cursor()
        if name is None and  id is None:
            cursor.execute("SELECT cid, name, description FROM client")

        elif name is not None and id is None:
            cursor.execute("SELECT cid, name, description FROM client WHERE name LIKE ?", (name,))

        elif id is not None and name is None:
            cursor.execute("SELECT cid, name, description FROM client WHERE cid = ?", (id,))

        else:
            #Invalid parameters passed
            return 'invalid'
    
        data = cursor.fetchall()
        result = []
        for application in data:
            result.append({
                'Id': application[0],
                'ApplicationName': application[1],
                'Description': application[2]
            })

        return result
    
    def remove_application(self, id: int) -> dict:

        #get the cid of the client
        cursor = self.database.cursor()
        cursor.execute("SELECT name FROM client WHERE cid = ?", (id,))
        name = cursor.fetchone()

        if(name):
            #remove the client
            cursor.execute("DELETE FROM client WHERE cid = ?", (id,))
            self.database.commit()

            return True
        
        return False
    
    def add_application(self, name: str, description: str|None, authentication: str, actions: List[str]) -> dict:
        #check if the client exists
        cursor = self.database.cursor()
        cursor.execute("SELECT cid FROM client WHERE name LIKE ?", (name,))
        row = cursor.fetchone()

        if(row):
            print("Application already exists.")
            exit(1)

        client_id = str(uuid4())
        client_secret = str(uuid4())
        hasher = PasswordHasher()
        
        if(authentication == 'access_token'):
            expiry = datetime.timestamp(datetime.now() + timedelta(days=360))

            cursor.execute('INSERT INTO client (name, description, authentication, client_id, client_secret) VALUES (?, ?, ?, ?, ?)',
                           (name, description, authentication, client_id, hasher.hash(client_secret)))
            self.database.commit()

            # Get the cid of our last insert
            cursor.execute('SELECT cid FROM client WHERE client_id = ?', (client_id,))
            cid = cursor.fetchone()[0]

            for action in actions:
                cursor.execute('INSERT INTO action_client_map (cid, action) VALUES (?, ?)', (cid, action.lower()))
                self.database.commit()

            access_token = jwt.encode({'reference': cid, 'expiry': expiry}, SECRET_KEY, algorithm='HS512')

            return {'access_token': access_token}
        
        elif(authentication == 'client_credential'):
            cursor.execute('INSERT INTO client (name, description, authentication, client_id, client_secret) VALUES (?, ?, ?, ?, ?)',
                           (name, description, authentication, client_id, hasher.hash(client_secret)))
            self.database.commit()

            # Get the cid of our last insert
            cursor.execute('SELECT cid FROM client WHERE client_id = ?', (client_id,))
            cid = cursor.fetchone()[0]

            for action in actions:
                cursor.execute('INSERT INTO action_client_map (cid, action) VALUES (?, ?)', (cid, action))
                self.database.commit()

            return {'client_id': client_id, 'client_secret': client_secret}
        
        else:
            print("Invalid authentication method.")
            exit(1)
    
    def set_application(self, cid: str, description: str|None, actions: List[str]|None) -> dict:
        cursor = self.database.cursor()

        if(description):
            print("Updating description")
            cursor.execute("UPDATE client SET description = ? WHERE cid = ?", (description, cid))
            self.database.commit()

        if(actions is not None):
            cursor.execute("DELETE FROM action_client_map WHERE cid = ?", (cid,))
            self.database.commit()

            for action in actions:
                cursor.execute('INSERT INTO action_client_map (cid, action) VALUES (?, ?)', (cid, action))
                self.database.commit()

        return True
