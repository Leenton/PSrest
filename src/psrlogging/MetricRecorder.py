from typing import Protocol
from psrlogging.Metric import Metric
from enum import Enum
from time import sleep
import sqlite3
import os
from configuration.Config import METRIC_DATABASE, setup_metric_db
from multiprocessing import Queue

class MetricRecorder(Protocol):
    def record(self, metric: Metric) -> None:
        ...

class MetricType(Enum):
    GAUGE = 1
    COUNTER = 2
    HISTOGRAM = 3
    SUMMARY = 4
    UNTYPED = 5
    INFO = 6
    STATESET = 7
    STATEGROUP = 8
    STRING = 9
    STRINGMAP = 10
    STRINGMAPENTRY = 11
    HISTOGRAMBUCKET = 12
    SUMMARYQUANTILE = 13
    LABELNAME = 14
    LABELVALUE = 15
    XXX_UNRECOGNIZED = 16

class PSRestMetrics(object):
    def __init__(self) -> None:
        self.db = sqlite3.connect(METRIC_DATABASE)

    def record(self, metric: Metric) -> None:
        #TODO: Implement this store this in the metrics database
        pass

    def run(self, stats: Queue) -> None:
        while True:
            try:
                metric: Metric = Metric(stats.get(False))
                self.record(metric)
            
            except Exception:
                sleep(0.1)

def start_metrics(queue: Queue) -> None:
    if(not os.path.exists(METRIC_DATABASE)):
        setup_metric_db()

    metrics = PSRestMetrics()
    metrics.run(queue)