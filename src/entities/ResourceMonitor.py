import sqlite3
from datetime import datetime
from psrlogging.Metric import MetricLabel
import psutil
from enum import Enum
from time import sleep
from configuration.Config import METRIC_DATABASE


class ResourceMonitor(object):
    def __init__(self) -> None:
        self.db = sqlite3.connect(METRIC_DATABASE)

    def get_resource_stats(self, time_period: int = 300) -> dict:
        return {
            'CPU_USAGE': self.get_cpu_usage(time_period),
            'MEMORY_USSAGE': self.get_memory_usage(time_period),
            'SHELL_SESSIONS': self.get_shell_sessions(time_period)
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
                SELECT COUNT(metric.created), metric.created FROM labels
                INNER JOIN metric ON labels.metric_id = metric.metric_id
                WHERE label = ?
                AND created > ?
                AND created < ?
                GROUP BY metric.created
                """,
                (label.value, now - time_period - 1, now + 1))
            traffic[label.name] = {}
            stats = cursor.fetchall()

            y = 300 
            for x in range(now - time_period, now):
                #get the number of requests for this second
                stat = 0
                for i in stats:
                    if i[1] == x + 1:
                        stat = i[0]
                        break

                traffic[label.name][y] = stat
                y -= 1
            
        return traffic
        
    def get_cpu_usage(self, time_period: int) -> list:
        now = int(datetime.timestamp(datetime.now()))
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT value, created FROM resource WHERE resource = ? AND created > ? AND created < ?",
            (MetricLabel.CPU_USAGE.value, now - time_period - 1, now + 1)
        )
        return cursor.fetchall()

    def get_memory_usage(self, time_period: int) -> list:
        now = int(datetime.timestamp(datetime.now()))
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT value, created FROM resource WHERE resource = ? AND created > ? AND created < ?",
            (MetricLabel.MEMORY_USAGE.value, now - time_period - 1, now + 1)
        )
        return cursor.fetchall()

    def get_shell_sessions(self, time_period: int) -> list:
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT COUNT(label) FROM labels WHERE label = ?",
            (MetricLabel.SHELL_UP.value,)
        )
        shell_up = cursor.fetchone()[0]

        cursor = self.db.cursor()
        cursor.execute(
            "SELECT COUNT(label) FROM labels WHERE label = ?",
            (MetricLabel.SHELL_DOWN.value,)
        )
        shell_down = cursor.fetchone()[0]

        shells = shell_up - shell_down

        return shells

    def start(self):
        while True:
            now = int(datetime.timestamp(datetime.now()))
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().used
            cursor = self.db.cursor()
            
            cursor.execute(
                "INSERT INTO resource (resource, value, created) VALUES (?, ?, ?)",
                (MetricLabel.CPU_USAGE.value, cpu_usage, now)
            )
            self.db.commit()

            cursor.execute(
                "INSERT INTO resource (resource, value, created) VALUES (?, ?, ?)",
                (MetricLabel.MEMORY_USAGE.value, memory_usage, now)
            )
            self.db.commit()

            sleep(1)

def start_resource_monitor() -> None:
    monitor = ResourceMonitor()
    monitor.start()