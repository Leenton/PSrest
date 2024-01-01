from queue import Queue
from typing import Callable
from .Ticket import Ticket

class Schedule():
    def __init__(self) -> None:
        self.scheudle: Queue[Ticket] = Queue()

    def add(self, ticket: Ticket) -> None:
        '''
        Adds a ticket to the schedule.
        '''
        self.scheudle.put(ticket)

    def get(self) -> Ticket:
        '''
        Returns the next ticket in the schedule and removes it from the schedule
        or None if the schedule is empty.
        '''        
        return self.scheudle.get_nowait()
    
    def peek(self) -> Ticket | None:
        '''
        Returns the next ticket in the schedule without removing it from the schedule.
        '''
        if(self.empty()):
            return None
        
        return self.scheudle.queue[0]
    
    def empty(self) -> bool:
        return self.scheudle.qsize() == 0

    def filter(self, *filters: Callable[[Ticket|None], Ticket|None]) -> None:
        '''
        Filters the schedule using the given filters.
        '''
        try:
            new_schedule: Queue[Ticket] = Queue()

            while(not self.empty()):
                ticket = self.scheudle.get_nowait()
                for filter in filters:
                    ticket = filter(ticket)
                
                if(ticket != None):
                    new_schedule.put(ticket)
            
            self.scheudle = new_schedule
        except Exception as e:
            print(e)
            exit(1)