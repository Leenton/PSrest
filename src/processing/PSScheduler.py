from entities.Cmdlet import Cmdlet
from entities.PSTicket import PSTicket
from entities.PSRestQueue import PSRestQueue
import asyncio
import json
import subprocess

class PSScheduler():
    '''
    This class is a singleton, that is used to schedule powershell jobs.
    '''
    __instance = None

    def __new__(cls):
        if(cls.__instance is None):
            cls.__instance = super(PSScheduler, cls).__new__(cls)
        return cls.__instance


    def __init__(self) -> None:
        self.schedule = {}
        self.PSProcessQueue = PSRestQueue()

    def request(self, command: Cmdlet) -> PSTicket|None:
        '''
        This method is used to request a powershell job to be executed.
        '''
        ticket = PSTicket()

        #Put the command in the schedule, it will be picked up for processing by the PSProcessor later.
        self.schedule[PSTicket.id] = command
        try:
            asyncio.run(self.PSProcessQueue.put(
                f'{command.platform}{command.psversion}{command.runas}',
                json.dumps({'command': command.serliaise(), 'ticket': ticket.id})
            ))
            return ticket
        except Exception as e:
            #TODO: Log this error
            print(e)
            return None

        

    def handleProcessors(self):
        subprocess.Popen(['powershell', 'Start-PSRestProcessor -ChannelName "PSRestQueue" -PSVersion "5.1" -Platform "Windows" -RunAs "System" -PublicKey "C:\\Users\\Public\\Documents\\PSRest\\PSRest.pub"'])
        '''
        This method is used to handle the powershell processors. ie start new ones, kill old ones, etc.
        '''
        pass
        
'''
The idea is simple, we launch as many simultanius powershell sessions we can get away with, and start and jobs on different powershell sessions/ processes

we have 1 process that generates jobs from commands that are sent to the user. 

1 process that executes these jobs, 

1 process that retrives the state of all the jobs, and puts the status into a QUE

Each request, basically puts a job on a queue, then just waits around on the job queue, for a job that looks like theirs (matching ID)

This job is then taken by python and formated into a valid response for the end user. 
'''