import sqlite3
from datetime import datetime
from log.Metric import Label
import psutil
from time import sleep
from aiosqlite import connect, Connection as AioConnection
from entities import ProcessorConnection
from configuration import METRIC_DATABASE

class ResourceMonitor(object):
    async def get_utilisation(self, start: int, end: int) -> dict:
        db = await connect(METRIC_DATABASE)
        usage = {
            'cpu': await self.get_cpu_usage(start, end, db),
            'memory': await self.get_memory_usage(start, end, db),
            'shells': await self.get_shell_sessions(start, end, db),
            'traffic': await self.get_traffic(start, end, db)
        }
        await db.close()

        return usage

    async def get_traffic(self, start: int, end: int, db: AioConnection) -> list:
        traffic = {}
        for label in [Label.REQUEST, Label.UNEXPECTED_ERROR, Label.INVALID_CREDENTIALS_ERROR, Label.UNAUTHORISED_ERROR, Label.BAD_REQUEST_ERROR]:
            cursor = await db.execute(f"""--sql
                SELECT COUNT(metric.created),  metric.created FROM labels
                INNER JOIN metric ON labels.metric_id = metric.metric_id
                WHERE label = {label.value}
                AND created <= {start}
                AND created >= {end}
                GROUP BY metric.created
                ORDER BY metric.created DESC
                """)
            traffic[label.name] = await cursor.fetchall()
        
        await cursor.close()
        return traffic
        
    async def get_cpu_usage(self, start: int, end: int, db: AioConnection) -> list:
        cursor = await db.execute(f"""--sql
            SELECT value, created FROM resource
            WHERE resource = {Label.CPU_USAGE.value}
            AND created <= {start}
            AND created >= {end}
            ORDER BY created DESC
            """)
        
        data = await cursor.fetchall()
        await cursor.close()
        return data

    async def get_memory_usage(self, start: int, end: int, db: AioConnection) -> list:
        cursor = await db.execute(f"""--sql
            SELECT value, created FROM resource
            WHERE resource = {Label.MEMORY_USAGE.value}
            AND created <= {start}
            AND created >= {end}
            ORDER BY created DESC
            """)
  
        data = await cursor.fetchall()
        await cursor.close()
        return data

    async def get_shell_sessions(self, start: int, end: int, db: AioConnection) -> list:
        cursor = await db.execute(f"""--sql
            SELECT value, created FROM resource
            WHERE resource = {Label.SHELLS.value}
            AND created <= {start}
            AND created >= {end}
            ORDER BY created DESC
            """)
        
        data = await cursor.fetchall()
        await cursor.close()
        return data

    def monitor(self):
        db = sqlite3.connect(METRIC_DATABASE)

        while True:
            now = int(datetime.timestamp(datetime.now()))
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().used
            cursor = db.cursor()
            
            cursor.execute(
                "INSERT INTO resource (resource, value, created) VALUES (?, ?, ?)",
                (Label.CPU_USAGE.value, cpu_usage, now)
            )
            db.commit()

            cursor.execute(
                "INSERT INTO resource (resource, value, created) VALUES (?, ?, ?)",
                (Label.MEMORY_USAGE.value, memory_usage, now)
            )
            db.commit()

            soc = (ProcessorConnection()).connect_sync()
            soc.send(b's')
            data = soc.recv(32)

            cursor.execute(
                "INSERT INTO resource (resource, value, created) VALUES (?, ?, ?)",
                (Label.SHELLS.value, data.decode(), now)
            )
            db.commit()

            sleep(1)

def start_resource_monitor() -> None:
    try:
        monitor = ResourceMonitor()
        monitor.monitor()
    except KeyboardInterrupt:
        exit(0)