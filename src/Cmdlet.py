import subprocess
import asyncio

class Cmdlet():
    
    def __init__(self, platform, psversion, command, user='current_user') -> None:
        self.platform = platform
        self.psversion = psversion
        self.command = self.parse(command)
        self.runas = user

    async def run(self):
        #depending on platfrom we could maybe switch the host we execute the command on, 
        #we 
        completed = subprocess.run(["pwsh", "-Command", self.command], capture_output=True)
        print(completed)

    def parse(self, command):
        return """write-host 'hello world'"""

command = Cmdlet('macOS', '7.3.1', 'write-host hello world string from URL')

async def process(command: Cmdlet):
    for x in range(10):
        await command.run()




import time
s = time.perf_counter()
asyncio.run(process(command))
elapsed = time.perf_counter() - s
print(f"{__file__} executed in {elapsed:0.2f} seconds.")


