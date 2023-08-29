import sqlite3
from datetime import datetime
from psrlogging.Metric import MetricLabel
import psutil
from enum import Enum
from time import sleep


class ResourceMonitor(object):
    def __init__(self) -> None:
        self.db = sqlite3.connect('resource_monitor.db')

    def get_resource_stats(self, time_period: int = 300) -> dict:
        return {
            'cpu': self.get_cpu_usage(time_period),
            'memory': self.get_memory_usage(time_period)
        }

    def get_traffic_stats(self, time_period: int = 300) -> list:
        now = int(datetime.timestamp(datetime.now()))
        labels = [
            MetricLabel.REQUEST,
            MetricLabel.UNEXPECTED_ERROR,
            MetricLabel.INVALID_CREDENTIALS_ERROR,
            MetricLabel.UNAUTHORISED_ERROR,
            MetricLabel.BAD_REQUEST_ERROR
        ]
        traffic = {}

        for label in labels:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COUNT(metric.created) FROM labels
                INNER JOIN metric ON labels.metric_id = metric.metric_id
                GROUP BY metric.created
                WHERE label = ?
                AND created > ?
                AND created =< ?
                """,
                (label.value, now - time_period, now))
            traffic[label.name] = cursor.fetchall()
            
        return traffic
        
    def get_cpu_usage(self, time_period: int) -> list:
        now = int(datetime.timestamp(datetime.now()))
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT value, created FROM resource
            WHERE resource = ?
            AND created > ?
            AND created =< ?
            """,
            (MetricLabel.CPU_USAGE.value, now - time_period, now)
        )
        return cursor.fetchall()

    def get_memory_usage(self, time_period: int) -> list:
        now = int(datetime.timestamp(datetime.now()))
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT value, created FROM resource
            WHERE resource = ?
            AND created > ?
            AND created =< ?
            """,
            (MetricLabel.MEMORY_USAGE.value, now - time_period, now)
        )
        return cursor.fetchall()

    def start(self):
        while True:
            now = int(datetime.timestamp(datetime.now()))
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().used
            cursor = self.db.cursor()
            
            cursor.execute("INSERT INTO resource (resource, value, created) VALUES (?, ?, ?)",
                (MetricLabel.CPU_USAGE.value, cpu_usage, now)
            )
            self.db.commit()

            cursor.execute("INSERT INTO resource (resource, value, created) VALUES (?, ?, ?)",
                (MetricLabel.MEMORY_USAGE.value, memory_usage, now)
            )
            self.db.commit()

            sleep(1)

def start_resource_monitor() -> None:
    monitor = ResourceMonitor()
    monitor.start()