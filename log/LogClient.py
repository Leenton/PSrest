from queue import Queue
from json import dumps
from .Message import Message

class LogClient():
    """
    A client for logging messages and metrics to a queue.

    Attributes:
        messages (Queue): A queue for storing log messages.

    Methods:
        log: Logs a message to the message queue.
    """
    def __init__(self, messages: Queue) -> None:
        self.messages: Queue[str] = messages

    def log(self, message: Message) -> None:
        '''
        Logs a message to the message queue.
        '''
        self.messages.put(dumps(message.serialise()))