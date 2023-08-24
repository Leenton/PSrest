
from multiprocessing import Queue

from psrlogging.Logger import Logger
from psrlogging.LogMessage import LogMessage
from psrlogging.MetricRecorder import MetricRecorder
from psrlogging.Metric import Metric
from typing import Protocol

class MetricRecorderLogger(Logger, MetricRecorder, Protocol):
    ...

class MultiProcessSafeRecorderLogger(MetricRecorderLogger):
    def __init__(self, message_queue: Queue, stats_queue: Queue) -> None:
        self.message_queue = message_queue
        self.stats_queue = stats_queue

    def record(self, metric: Metric):
        self.stats_queue.put(metric)

    def log(self, message: LogMessage):
        self.message_queue.put(message)