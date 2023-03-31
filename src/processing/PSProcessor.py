from multiprocessing import Process, active_children, Queue
import subprocess
from uuid import uuid4

class PSProcessor():
    def __init__(self, kill_queue: Queue, request_overflow_queue: Queue, publickey: str) -> None:
        self.kill_queue = kill_queue
        self.request_overflow_queue = request_overflow_queue
        self.publickey = publickey

    def execute(self, id, platform = 'pwsh'):
        try:
            result = subprocess.run([f'{platform}', "-Command", f'start-sleep -s 60; write-host "slept"'] , stdout=subprocess.DEVNULL)
        except Exception as e:
            #TODO: Log this error
            print(e)
    
    def start(self, process_count: int, kill_queue: Queue, request_overflow_queue: Queue):
        for x in range(process_count):
            id = uuid4().hex
            Process(name=(f'PSRestProcessor {id}'), target=self.execute, args=(id,)).start()

        while(True):
            #if there are less processors running than we want, start a new one
            running_psrestprocessors = 0
            for child in active_children():
                if child.name.startswith('PSRestProcessor'):
                    running_psrestprocessors += 1
        
            if(running_psrestprocessors != process_count):
                id = uuid4().hex
                Process(name=(f'PSRestProcessor {id}'), target=self.execute, args=(id,)).start()
            
            #if we recieve a kill signal, kill the specified process
            if(not kill_queue.empty()):
                kill_child = kill_queue.get()
                for child in active_children():
                    if child.name == kill_child:
                        #TODO: Log this
                        #log how long the process was running for before it was killed
                        child.terminate()

            if(not request_overflow_queue.empty()):
                id = uuid4().hex
                Process(name=(f'PSRestProcessor {id}'), target=self.execute, args=(id,)).start()