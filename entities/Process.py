from datetime import datetime
from enum import Enum
import asyncio
import subprocess

from configuration.Config import *

class ProcessStatus(Enum):
    FREE = 0
    BUSY = 1
    KILL = 2

class Process():
    def __init__(self, pid: str, created: datetime, last_seen: datetime, platform = 'pwsh') -> None:
        self.pid = pid
        self.created = created
        self.last_seen = last_seen
        self.status = ProcessStatus.FREE
        self.current_ticket: str = None
        self.current_ticket_expiry: float = None
        self.platform = platform
        self.task: asyncio.Task = self.start()

    def start(self):
        return asyncio.create_task(self.execute())

    def terminate(self):
        self.task.cancel()

    async def execute(self):
        print('Starting process')
        if(PLATFORM == 'Windows'):
            cmd = f'{self.platform} -c \'Start-PSRestProcess -ProcessorId "{self.pid}" -ResponseSocket "{RESPONDER_ADDRESS}" -CmdletSourceSocket"{DISTRIBUTOR_ADDRESS}"\''
        else:
            cmd = f'{self.platform} -c \'Start-PSRestProcess -ProcessorId "{self.pid}" -ResponseSocket "{RESPONDER_UNIX_ADDRESS}" -CmdletSourceSocket "{DISTRIBUTOR_UNIX_ADDRESS}"\''
        
        print(cmd)
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.DEVNULL,
        )