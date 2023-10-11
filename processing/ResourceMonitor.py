import sqlite3
from datetime import datetime
from log.Metric import Label
import psutil
from time import sleep
from typing import Generator
from aiosqlite import connect, Connection as AioConnection
from entities import ProcessorConnection
from configuration import METRIC_DATABASE, METRIC_INTERVAL, MAX_METRIC_WAVE_LENGTH

class ResourceMonitor(object):
    def __init__(self) -> None:
        self.db: AioConnection = None

    async def get_utilisation(self, time_range: int) -> Generator[dict, None, None]:
        time_to_wave_length_ratio = time_range / MAX_METRIC_WAVE_LENGTH
        if(time_range < 60 or not isinstance(time_to_wave_length_ratio, int)):
            raise ValueError(f'The time range be greater than 60, or value between 60 and {MAX_METRIC_WAVE_LENGTH}, or a multiple of {MAX_METRIC_WAVE_LENGTH}.')

        if (time_to_wave_length_ratio <= 1):
            sleep_interval = 1
        else:
            sleep_interval = time_to_wave_length_ratio
        
        # Take a historical sample for the given time range.
        start = int(datetime.timestamp(datetime.now()))
        end = start - time_range
        temp_end = end

        samples = []
        while temp_end < start:
            temp_start = temp_end + sleep_interval
            sample = {
                'cpu': await self.get_cpu_usage(temp_start, temp_end),
                'memory': await self.get_memory_usage(temp_start, temp_end),
                'shells': await self.get_shell_sessions(temp_start, temp_end),
                'traffic': await self.get_traffic(temp_start, temp_end),
                'created': temp_start,
            }
            samples.append(sample)
            temp_end += sleep_interval
        
        self.db.close()
        yield samples

        # Take a sample for the given ratio period.        
        while True:
            await sleep(sleep_interval)

            start = start + sleep_interval
            end = start - time_range

            sample = {
                'cpu': await self.get_cpu_usage(start, end),
                'memory': await self.get_memory_usage(start, end),
                'shells': await self.get_shell_sessions(start, end),
                'traffic': await self.get_traffic(start, end),
                'created': start,
            }

            yield sample

    async def get_traffic(self, start: int, end: int) -> dict[str, int]:
        traffic = {}
        for label in [Label.REQUEST, Label.UNEXPECTED_ERROR, Label.INVALID_CREDENTIALS_ERROR, Label.UNAUTHORISED_ERROR, Label.BAD_REQUEST_ERROR]:
            load = await self.get_data(f"""--sql
                SELECT AVG(load) FROM (
                    SELECT COUNT(metric.created) AS load FROM labels
                    INNER JOIN metric ON labels.metric_id = metric.metric_id
                    WHERE label = {label.value}
                    AND created <= {start}
                    AND created >= {end}
                ) traffic
            """)
            traffic[label.name] = load

        return traffic
    
    async def get_data(self, sql: str) -> int:
        db = await connect(METRIC_DATABASE)
        cursor = await self.db.execute(sql)
        data = await cursor.fetchone()[0]
        await cursor.close()
        await db.close()

        if(data == None):
            data = 0

        return data
    
    async def get_cpu_usage(self, start: int, end: int) -> int:
        return await self.get_data(f"""--sql
            SELECT AVG(value) FROM resource
            WHERE resource = {Label.CPU_USAGE.value}
            AND created < {start}
            AND created >= {end}
        """)

    async def get_memory_usage(self, start: int, end: int) -> int:
        return await self.get_data(f"""--sql
            SELECT AVG(value) FROM resource
            WHERE resource = {Label.MEMORY_USAGE.value}
            AND created < {start}
            AND created >= {end}
        """)

    async def get_shell_sessions(self, start: int, end: int) -> int:
        return await self.get_data(f"""--sql
            SELECT AVG(value) FROM resource
            WHERE resource = {Label.SHELLS.value}
            AND created < {start}
            AND created >= {end}
        """)

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

            sleep(METRIC_INTERVAL)

def start_resource_monitor() -> None:
    try:
        monitor = ResourceMonitor()
        monitor.monitor()
    except KeyboardInterrupt:
        exit(0)