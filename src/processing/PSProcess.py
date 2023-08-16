import subprocess
from Config import *
from uuid import uuid4

class PSProcess():
    def __init__(self, platform = 'pwsh'):
        self.id = uuid4().hex
        self.platform = platform

    def execute(self):
        try:
            completed = result = subprocess.run(
                [
                    f'{self.platform}',
                    "-Command",
                    f'Start-PSRestProcessor -ProcessorId "{self.id}" -ResponseDirectory "{RESPONSE_DIR}" -SocketPath "{PSRESTQUEUE_SRV}" -WaitTime {PSRESTQUEUE_WAIT}'
                ],
                stdout=subprocess.DEVNULL)
            print(completed)
        except Exception as e:
            #TODO: Log this error
            print(e)

        print("Fuck this shit we're out")