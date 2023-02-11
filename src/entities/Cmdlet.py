import subprocess
import asyncio
class Cmdlet():
    
    def __init__(self, platform, psversion, user, command, ttl=60) -> None:
        self.platform = platform
        self.psversion = psversion
        self.runas = user
        self.ttl = ttl

        command = self.parse(command)
        self.function = command['function']
        self.params = command['params']

    async def run(self):
        #depending on platfrom we could maybe switch the host we execute the command on, 
        #we 
        completed = subprocess.run(["pwsh", "-Command", self.command], capture_output=True)
        print(completed)

    def parse(self, command: dict) -> str:

        command_name = command['command']
        
        if(field == 'function'):
            self.function = command[field]
        elif(field == 'params'):
            self.params = command[field]
        
        return command


    def serliaise(self) -> dict:
        return {}

command = Cmdlet('macOS', '7.3.1', 'write-host hello world string from URL')

async def process(command: Cmdlet):
    for x in range(10):
        await command.run()




import time
s = time.perf_counter()
asyncio.run(process(command))
elapsed = time.perf_counter() - s
print(f"{__file__} executed in {elapsed:0.2f} seconds.")


