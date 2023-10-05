from typing import List
from multiprocessing import Queue
import sqlite3
from time import sleep
from json import loads
from uuid import uuid4
from .LogWriter import LogWriter
from configuration import METRIC_DATABASE

class Log():
    def __init__(self, messages: Queue, metrics: Queue) -> None:
        self.messages: Queue[str] = messages
        self.metrics: Queue[str] = metrics
        self.log_writer: LogWriter = LogWriter()
        self.db = sqlite3.connect(METRIC_DATABASE)

    def log(self, message: dict) -> None:
        self.log_writer.write(message)
    
    def record(self, metric: dict[str, str|List[int]]) -> None:
        metric_id = uuid4().hex
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO metric (metric_id, created) VALUES (?, ?)",
            (metric_id , metric['created'])
        )
        self.db.commit()

        for label in metric['labels']:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO labels (metric_id, label) VALUES (?, ?)",
                (metric_id, label)
            )
            self.db.commit()


    def run(self) -> None:
        while True:
            try:
                message: dict[str] = loads(self.messages.get(False))
                self.log(message)
                logged_messages = True
            except Exception:
                logged_messages = False

            try:
                metric: dict[str] = loads(self.metrics.get(False))
                self.record(metric)
                logged_metrics = True
            except Exception:
                logged_metrics = False

            if not logged_messages and not logged_metrics:
                sleep(0.01)


def start_logging(messages: Queue[str], metrics: Queue[str]) -> None:
    try:
        log = Log(messages, metrics)
        log.run()
    except KeyboardInterrupt:
        exit(0)