
from multiprocessing import Queue
from typing import Protocol

from log.Logger import Logger
from log.LogMessage import LogMessage
from log.MetricRecorder import MetricRecorder
from log.Metric import Metric

class MetricRecorderLogger(Logger, MetricRecorder, Protocol):
    ...

class MultiProcessSafeRecorderLogger(MetricRecorderLogger):
    def __init__(self, message_queue: Queue = Queue(), stats_queue: Queue = Queue()) -> None:
        self.message_queue = message_queue
        self.stats_queue = stats_queue

    def record(self, metric: Metric):
        self.stats_queue.put(metric.serialise())

    def log(self, message: LogMessage):
        print(message.message)
        # self.message_queue.put(message.serialise())