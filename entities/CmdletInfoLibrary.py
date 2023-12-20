import subprocess
import json
import base64
import random
from configuration import CONFIG_FILE
from .CmdletInfo import CmdletInfo

class CmdletInfoLibrary():
    def __init__(self) -> None:
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
        #read the config file and get the list of modules to load amd allowed commands and etc
        seperator = random.randint(1_000_000_000, 9_999_999_999)

        result = subprocess.run(
            f'pwsh -c "Get-PSRestCommandLibrary -ConfigFile \'{CONFIG_FILE}\' -Seperator {seperator}"',
            shell=True,
            capture_output=True,
            text=True)

        result = base64.b64decode(result.stdout.split(str(seperator))[1])
        commands = json.loads(result)

        for command in commands:
            self.cmdlets[command['Name'].lower()] = CmdletInfo(
                command['Name'],
                command['MandatoryParameters'],
                command['Module'],
                command['Version'],
                command['Help'])
