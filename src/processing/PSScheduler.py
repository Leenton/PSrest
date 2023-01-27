from entities.Cmdlet import Cmdlet
from entities.PSTicket import PSTicket
from queue import Queue
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
        self.queue = Queue()
        self.PSProcesQueue = Queue()

    def request(self, command: Cmdlet) -> PSTicket:
        '''
        This method is used to request a powershell job to be executed.
        '''
        ticket = PSTicket()

        #Put the command in the schedule, it will be picked up for processing by the PSProcessor later.
        self.schedule[PSTicket.id] = command
        self.queue.put({'command': command.serliaise(), 'ticket': ticket.id})
        self.PSProcesQueue.put({'command': command.serliaise(), 'ticket': ticket.id})

        return ticket

    def handleProcessors(self):
        '''
        This method is used to handle the powershell processors.
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