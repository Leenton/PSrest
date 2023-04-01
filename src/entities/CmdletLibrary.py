from entities.CmdletInfo import CmdletInfo
import subprocess
import json
import base64
import random
from Config import *

class CmdletLibrary():
    def __init__(self) -> None:
        self.cmdlets = {}
        #create a temporary database to store the cmdlets in memory
        self.intialize()
    
    def get_cmdlet(self, cmdlet_name) -> CmdletInfo | None:
        try:
            cmdlet_info: CmdletInfo = self.cmdlets[cmdlet_name.lower()]
            return cmdlet_info
        except KeyError:
            return None
    
    def intialize(self) -> None:
        #read the config file and get the list of modules to load amd allowed commands and etc
        seperator = random.randint(1_000_000_000, 9_999_999_999)
        result = subprocess.run(
            f'pwsh -c "Get-PSRestCommandLibrary -Module {MODULES} -Seperator {seperator}"',
            shell=True,
            capture_output=True,
            text=True)
        # -EnabledCommands {ENABLE_COMMANDS} -DisabledCommands {DISABLE_COMMANDS} 

        result = base64.b64decode(result.stdout.split(str(seperator))[1])
        commands = json.loads(result)

        for command in commands:
            self.cmdlets[command['Name'].lower()] = CmdletInfo(
                command['Name'],
                command['MandatoryParameters'],
                command['Module'],
                command['Version'],
                command['Help'])
