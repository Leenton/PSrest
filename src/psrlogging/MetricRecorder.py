from typing import Protocol
from psrlogging.Metric import Metric, MetricLabel
from enum import Enum
from time import sleep
from typing import List
import sqlite3
from datetime import datetime
import os
from configuration.Config import METRIC_DATABASE, setup_metric_db
from multiprocessing import Queue
from uuid import uuid4

class MetricRecorder(Protocol):
    def record(self, metric: Metric) -> None:
        ...

class PSRestMetricHandler():
    def __init__(self) -> None:
        self.db = sqlite3.connect(METRIC_DATABASE)

    def record(self, labels: List[MetricLabel], created: int) -> None:
        metric_id = uuid4().hex
        cursor = self.db.cursor()
        cursor.execute(
            'INSERT INTO metric (metric_id, created) VALUES (?, ?)',
            (metric_id , created)
        )
        self.db.commit()

        #TODO: Fix this shit
        for label in labels:
            cursor = self.db.cursor()
            cursor.execute(
                'INSERT INTO label (metric_id, label) VALUES (?, ?)',
                (metric_id, label)
            )
            self.db.commit()

    def run(self, stats: Queue) -> None:
        while True:
            try:
                metric = (stats.get(False))
                self.record(
                    map((lambda label: MetricLabel(label)),metric['labels']),
                    metric['created']
                )

            except Exception as e:
                sleep(0.0025)

def start_metrics(queue: Queue) -> None:
    if(not os.path.exists(METRIC_DATABASE)):
        setup_metric_db()

    metrics = PSRestMetricHandler()
    metrics.run(queue)