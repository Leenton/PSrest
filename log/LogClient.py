from queue import Queue
from json import dumps
from .Message import Message
from .Metric import Metric

class LogClient():
    def __init__(self, messages: Queue, metrics: Queue) -> None:
        self.messages: Queue[str] = messages
        self.metrics: Queue[str] = metrics

    def log(self, message: Message) -> None:
        self.messages.put(dumps(message.serialise()))

    def record(self, metric: Metric) -> None:
        self.messages.put(dumps(metric.serialise()))
 