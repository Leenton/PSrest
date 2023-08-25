from typing import Protocol
from psrlogging.Metric import Metric
from enum import Enum
from time import sleep
import sqlite3
from datetime import datetime
import os
from configuration.Config import METRIC_DATABASE, setup_metric_db
from multiprocessing import Queue
from uuid import uuid4

class MetricRecorder(Protocol):
    def record(self, metric: Metric) -> None:
        ...

class PSRestMetrics(object):
    def __init__(self) -> None:
        self.db = sqlite3.connect(METRIC_DATABASE)

    def record(self, metric: Metric) -> None:
        labels: list = metric.get_labels()
        metric_id = uuid4().hex
        cursor = self.db.cursor()
        cursor.execute(
            'INSERT INTO metric (metric_id, created) VALUES (?, ?)',
            (metric_id ,datetime.timestamp(datetime.now()))
        )
        self.db.commit()

        #TODO: Fix this shit
        for label in labels:
            cursor = self.db.cursor()
            cursor.execute(
                'INSERT INTO label (metric_id, name) VALUES (?, ?)',
                (metric_id, label)
            )
            self.db.commit()

    def run(self, stats: Queue) -> None:
        while True:
            try:
                metric: Metric = Metric(stats.get(False))
                self.record(metric)

            except Exception as e:
                sleep(0.1)

def start_metrics(queue: Queue) -> None:
    if(not os.path.exists(METRIC_DATABASE)):
        setup_metric_db()

    metrics = PSRestMetrics()
    metrics.run(queue)