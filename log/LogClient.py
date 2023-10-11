from queue import Queue
from json import dumps
from .Message import Message
from .Metric import Metric

class LogClient():
    """
    A client for logging messages and metrics to a queue.

    Attributes:
        messages (Queue): A queue for storing log messages.
        metrics (Queue): A queue for storing log metrics.

    Methods:
        log: Logs a message to the message queue.
        record: Records a metric to the metric queue.
    """
    def __init__(self, messages: Queue, metrics: Queue) -> None:
        self.messages: Queue[str] = messages
        self.metrics: Queue[str] = metrics

    def log(self, message: Message) -> None:
        '''
        Logs a message to the message queue.
        '''
        self.messages.put(dumps(message.serialise()))

    def record(self, metric: Metric) -> None:
        '''
        Records a metric to the metric queue.
        '''
        self.metrics.put(dumps(metric.serialise()))
 