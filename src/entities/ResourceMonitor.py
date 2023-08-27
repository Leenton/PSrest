import sqlite3
from datetime import datetime
from psrlogging.Metric import MetricLabel
class ResourceMonitor(object):
    def __init__(self) -> None:
        self.db = sqlite3.connect('resource_monitor.db')

    def get_resource_stats(self) -> float:
        #query db for the stats
        pass

    def get_traffic_stats(self, time_period: int = 60) -> list:
        cursor = self.db.cursor()
        cursor.execute("""--sql
            SELECT name, created FROM labels
            INNER JOIN metric ON labels.metric_id = metric.metric_id
            WHERE name = ?
            AND created > ?
            """,
            (MetricLabel.REQUEST.value,  int(datetime.timestamp(datetime.now)) - time_period))
        total_requests = cursor.fetchone()

        

    def get_cpu_usage(self) -> float:
        pass

    def get_memory_usage(self) -> float:
        pass

    def start(self):
        while True:
            #get the cpu ussage and log it to the db 
            #get the memory usage and log it to the db
            pass

def start_resource_monitor() -> None:
    monitor = ResourceMonitor()
    monitor.start()