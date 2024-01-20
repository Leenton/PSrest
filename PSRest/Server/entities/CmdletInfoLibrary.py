import subprocess
import random
from configuration.Console import get_actions
from configuration import CREDENTIAL_DATABASE, PSREST_CMDLETS
from .CmdletInfo import CmdletInfo
from sqlite3 import connect
from json import loads, dumps
from base64 import b64encode, b64decode

class CmdletInfoLibrary():
    def __init__(self) -> None:
        self.db = connect(CREDENTIAL_DATABASE)
        self.cmdlets: dict[CmdletInfo] = {}
        #create a temporary database to store the cmdlets in memory
        self.intialize()
    
    def get_cmdlet(self, cmdlet_name: str) -> CmdletInfo | None:
        try:
            cmdlet_info: CmdletInfo = self.cmdlets[cmdlet_name.lower()]
            return cmdlet_info
        except KeyError:
            return None

    def get_cmdlets(self) -> list[str]:
        cmdlets = []
        for key, value in self.cmdlets.items():
            cmdlets.append(value.command)

        return cmdlets
    
    def intialize(self) -> None:
        # Build the action_client_map table in the database
        cursor = self.db.cursor()
        cursor.executescript(
            "DROP TABLE IF EXISTS action_client_map;"
        )

        cursor.executescript(
            "CREATE TABLE action_client_map (aid INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid) ON DELETE CASCADE);"
        )

        cursor.execute(
            "SELECT cid, enabled_cmdlets, disabled_cmdlets, enabled_modules FROM client"
        )
        data = cursor.fetchall()

        for row in data:
            actions = get_actions(row[1], row[2], row[3])
            for action in actions:
                cursor.execute(
                    "INSERT INTO action_client_map (action, cid) VALUES (?, ?)",
                    (action, row[0])
                )

                self.db.commit()
        
        # Build the cmdlet library in memory
        cursor.execute(
            "SELECT DISTINCT action FROM action_client_map"
        )

        data = cursor.fetchall()
        cmdlets = []

        for row in data:
            cmdlets.append(row[0])
        
        for cmdlet in PSREST_CMDLETS:
            cmdlets.append(cmdlet)

        #Make contents of cmdlets unique
        cmdlets = list(set(cmdlets))
        
        
        if (cmdlets):
            separator = random.randint(1_000_000_000, 9_999_999_999)
            enabled = b64encode(dumps(cmdlets).encode('utf-8')).decode('utf-8')
    
            result = subprocess.run(
                f'pwsh -c "Get-PSRestCommandLibrary -Enabled \'{enabled}\' -Separator {separator} -AsBase64"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            result = b64decode(result.stdout)
            commands = loads(result)

            for command in commands:
                self.cmdlets[command['Name'].lower()] = CmdletInfo(
                    command['Name'],
                    command['MandatoryParameters'],
                    command['Module'],
                    command['Version'],
                    command['Help'])
