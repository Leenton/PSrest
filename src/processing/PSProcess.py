import subprocess
from Config import RESPONSE_DIR, PSRESTQUEUE_PUT
from uuid import uuid4

class PSProcess():
    def __init__(self, platform = 'pwsh'):
        self.id = uuid4().hex
        self.platform = platform

    def execute(self):
        try:
            result = subprocess.run(
                [f'{self.platform}', "-Command", f'Start-PSRestProcessor -ProcessId "{self.id}" -ResponsePath "{RESPONSE_DIR}" -SocketPath "{PSRESTQUEUE_PUT}""'],
                stdout=subprocess.DEVNULL)
        except Exception as e:
            #TODO: Log this error
            print(e)