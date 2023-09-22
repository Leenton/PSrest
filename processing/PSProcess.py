import subprocess
from configuration.Config import *
from uuid import uuid4
from log.MetricRecorderLogger import MetricRecorderLogger
from log.Metric import Metric, MetricLabel

class PSProcess():
    def __init__(self, platform = 'pwsh'):
        self.id = uuid4().hex
        self.platform = platform

    def execute(self):
        try:
            print(f'Start-PSRestProcessor -ProcessorId "{self.id}" -ResponseDirectory "{RESPONSE_DIR}" -SocketPath "{PSRESTQUEUE_SRV}" -WaitTime {PSRESTQUEUE_WAIT}')
            result = subprocess.run(
                [
                    f'{self.platform}',
                    "-Command",
                    f'Start-PSRestProcessor -ProcessorId "{self.id}" -ResponseDirectory "{RESPONSE_DIR}" -SocketPath "{PSRESTQUEUE_SRV}" -WaitTime {PSRESTQUEUE_WAIT}'
                ],
                stdout=subprocess.DEVNULL)
        except Exception as e:
            #TODO: Log this error
            print(e)