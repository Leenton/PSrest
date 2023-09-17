from typing import Protocol
from log.Metric import Metric, MetricLabel
from time import sleep
from typing import List
import sqlite3
from configuration.Config import METRIC_DATABASE
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
            "INSERT INTO metric (metric_id, created) VALUES (?, ?)",
            (metric_id , created)
        )
        self.db.commit()

        for label in labels:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO labels (metric_id, label) VALUES (?, ?)",
                (metric_id, label.value)
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
                sleep(0.1)

def start_metrics(queue: Queue) -> None:
    try:
        metrics = PSRestMetricHandler()
        metrics.run(queue)
    except KeyboardInterrupt:
        exit(0)
