import sqlite3
import jwt
from argon2 import PasswordHasher
import sqlite3
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4
from .Config import * 
import subprocess
import random
from base64 import b64encode, b64decode
from json import loads

def get_actions(enabled: str, disabled: str, modules: str) -> List[str]:
    separator = random.randint(1_000_000_000, 9_999_999_999)
    filter = b64encode(f'{enabled}{separator}{modules}{separator}{disabled}'.encode('utf-8')).decode('utf-8')
    result = subprocess.run(
        f'pwsh -c "Get-PSRestActions -Filter \'{filter}\' -Separator {separator}" -AsBase64',
        shell=True,
        capture_output=True,
        text=True
    )

    cmdlets = loads(b64decode(result.stdout).decode('utf-8'))

    return cmdlets

class Console():
    def __init__(self,) -> None:
        self.service = 1
        self.database = sqlite3.connect(CREDENTIAL_DATABASE)

    def run(self, request: dict) -> dict:
        if request['method'] == 'add':
            return self.add_application(
                request['name'],
                request['description'],
                request['authentication'],
                request['enabledActions'],
                request['enabledModules'],
                request['disabledActions']
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
                request.get('enabledActions', None),
                request.get('enabledModules', None),
                request.get('disabledActions', None)
            )
        
        elif request['method'] == 'version':
            return self.get_version()
        
        elif request['method'] == 'config':
            return self.get_config()
    
    def get_application(self, name: str|None = None, id: int|None = None) -> dict:
        cursor = self.database.cursor()
        if name is None and  id is None:
            cursor.execute("SELECT cid, name, description, enabled_cmdlets, disabled_cmdlets, enabled_modules FROM client")

        elif name is not None and id is None:
            cursor.execute(
                "SELECT cid, name, description, enabled_cmdlets, disabled_cmdlets, enabled_modules FROM client WHERE name LIKE ?",
                (name,))

        elif id is not None and name is None:
            cursor.execute(
                "SELECT cid, name, description, enabled_cmdlets, disabled_cmdlets, enabled_modules FROM client WHERE cid = ?",
                (id,))

        else:
            # Invalid parameters passed
            return 'invalid'
    
        data = cursor.fetchall()
        result = []
        for application in data:
            result.append({
                'Id': application[0],
                'ApplicationName': application[1],
                'Description': application[2],
                'EnabledCmdlets': application[3].split(','),
                'DisabledModuleCmdlets': application[4].split(','),
                'EnabledModules': application[5].split(',')
            })

        return result
    
    def remove_application(self, id: int) -> dict:

        # Get the cid of the client
        cursor = self.database.cursor()
        cursor.execute(
            "SELECT name FROM client WHERE cid = ?",
            (id,))
        name = cursor.fetchone()

        if(name):
            # Remove the client
            cursor.execute(
                "DELETE FROM client WHERE cid = ?",
                (id,))
            self.database.commit()

            return True
        
        return False
    
    def add_application(
            self,
            name: str,
            description: str|None,
            authentication: str,
            enabled: List[str],
            modules: List[str],
            disabled: List[str]
        ) -> dict:
        
        # Check if the client exists
        cursor = self.database.cursor()
        cursor.execute(
            "SELECT cid FROM client WHERE name LIKE ?",
            (name,))
        
        row = cursor.fetchone()

        if(row):
            print("Application already exists.")
            exit(1)

        client_id = str(uuid4())
        client_secret = str(uuid4())
        hasher = PasswordHasher()
        
        if(authentication == 'access_token'):
            expiry = datetime.timestamp(datetime.now() + timedelta(days=365))

            cursor.execute(
                "INSERT INTO client (name, description, authentication, client_id, client_secret, enabled_cmdlets, disabled_cmdlets, enabled_modules) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, description, authentication, client_id, hasher.hash(client_secret), ','.join(enabled), ','.join(disabled), ','.join(modules))
            )
            self.database.commit()

            # Get the cid of our last insert
            cursor.execute(
                "SELECT cid FROM client WHERE client_id = ?",
                (client_id,))

            cid = cursor.fetchone()[0]

            access_token = jwt.encode({'reference': cid, 'expiry': expiry}, SECRET_KEY, algorithm='HS512')

            return {'access_token': access_token}
        
        elif(authentication == 'client_credential'):
            cursor.execute(
                "INSERT INTO client (name, description, authentication, client_id, client_secret, enabled_cmdlets, disabled_cmdlets, enabled_modules) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, description, authentication, client_id, hasher.hash(client_secret), ','.join(enabled), ','.join(disabled), ','.join(modules))
            )

            self.database.commit()

            return {'client_id': client_id, 'client_secret': client_secret}
        
        else:
            print("Invalid authentication method.")
            exit(1)
    
    def set_application(
            self, cid: str,
            description: str|None,
            enabled: List[str]|None = None,
            modules: List[str]|None = None,
            disabled: List[str]|None = None
        ) -> dict:
        cursor = self.database.cursor()

        if(description):
            cursor.execute(
                "UPDATE client SET description = ? WHERE cid = ?",
                (description, cid))
            
            self.database.commit()
        
        if enabled is not None:
            cursor.execute(
                "UPDATE client SET enabled_cmdlets = ? WHERE cid = ?",
                (','.join(enabled), cid))
            
            self.database.commit()

        if disabled is not None:
            cursor.execute(
                "UPDATE client SET disabled_cmdlets = ? WHERE cid = ?",
                (','.join(disabled), cid))
            
            self.database.commit()
        
        if modules is not None:
            cursor.execute(
                "UPDATE client SET enabled_modules = ? WHERE cid = ?",
                (','.join(modules), cid))
            
            self.database.commit()

        return True

    def get_version(self) -> dict:
        return {'version': VERSION}
    
    def get_config(self) -> dict:
        return {
            'path': APP_DATA,
            'version': VERSION,
            'platform': PLATFORM
        }
