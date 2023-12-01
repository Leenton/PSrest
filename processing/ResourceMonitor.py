import sqlite3
from datetime import datetime
from log.Metric import Label
import psutil
from time import sleep
from asyncio import sleep as async_sleep
from typing import Generator
from aiosqlite import connect, Connection as AioConnection
from entities import ProcessorConnection
from configuration import METRIC_DATABASE, METRIC_INTERVAL, MAX_METRIC_WAVE_LENGTH, CLEAR_OLD_METRICS
from queue import Queue

class ResourceMonitor(object):
    async def get_utilisation(self, time_range: int) -> Generator[dict, None, None]:
        if(time_range < 60):
            raise ValueError(f'The time range be greater than 60, or value between 60 and {MAX_METRIC_WAVE_LENGTH}, or a multiple of {MAX_METRIC_WAVE_LENGTH}.')

        time_to_wave_length_ratio = time_range / MAX_METRIC_WAVE_LENGTH

        if(MAX_METRIC_WAVE_LENGTH < time_range  and not time_to_wave_length_ratio.is_integer()):
            raise ValueError(f'The time range be greater than 60, or value between 60 and {MAX_METRIC_WAVE_LENGTH}, or a multiple of {MAX_METRIC_WAVE_LENGTH}.')

        if (time_to_wave_length_ratio <= 1):
            sleep_interval = 1
        else:
            sleep_interval = time_to_wave_length_ratio
        

        # Get historic metric data for the given time range.

        start = int(datetime.timestamp(datetime.now()))
        db = await connect(METRIC_DATABASE)
        raw_data = await self.get_bulk_data(time_range, start, db)
        bulk_data = {}
        bulk_data['created'] = start
        bulk_data['range'] = time_range
        bulk_data['interval'] = sleep_interval
        for key in raw_data:
            bulk_data[key] = await self.down_sample_data(raw_data[key], time_range, sleep_interval, start)

        await db.close()
        yield bulk_data

        # Take a sample for the given ratio period.        
        while True:
            await async_sleep(sleep_interval)
            db = await connect(METRIC_DATABASE)
            end = start
            start = start + sleep_interval

            sample = {
                'cpu': await self.get_cpu_usage(start, end, db),
                'memory': await self.get_memory_usage(start, end, db),
                'shells': await self.get_shell_sessions(start, end, db),
                'traffic': await self.get_traffic(start, end,  db),
                'created': start,
                'range': 1
            }

            await db.close() 
            yield sample

    async def get_bulk_data(self, time_range: int, start: int, db: AioConnection) -> dict:
        raw_data = {}
        end = start - time_range
        
        # Get cpu usage
        cursor = await db.execute(f"""--sql
            SELECT value, created FROM resource
            WHERE resource = {Label.CPU_USAGE.value}
            AND created < {start}
            AND created >= {end}
            ORDER BY created ASC
        """)
        raw_data['cpu'] = await cursor.fetchall()
        
        # Get memory usage
        cursor = await cursor.execute(f"""--sql
            SELECT value, created FROM resource
            WHERE resource = {Label.MEMORY_USAGE.value}
            AND created < {start}
            AND created >= {end}
            ORDER BY created ASC
        """)
        raw_data['memory'] = await cursor.fetchall()

        # Get shell sessions
        cursor = await cursor.execute(f"""--sql
            SELECT value, created FROM resource
            WHERE resource = {Label.SHELLS.value}
            AND created < {start}
            AND created >= {end}
            ORDER BY created ASC
        """)
        raw_data['shells'] = await cursor.fetchall()

        raw_data['traffic'] = {}
        # Get traffic
        for label in [Label.REQUEST, Label.UNEXPECTED_ERROR, Label.INVALID_CREDENTIALS_ERROR, Label.UNAUTHORISED_ERROR, Label.BAD_REQUEST_ERROR]:
            cursor = await cursor.execute(f"""--sql
                SELECT COUNT(metric.created) AS load, metric.created FROM labels
                INNER JOIN metric ON labels.metric_id = metric.metric_id
                WHERE label = {label.value}
                AND created <= {start}
                AND created >= {end}
                GROUP BY metric.created
                ORDER BY metric.created ASC 
            """)

            raw_data['traffic'][label.name] = await cursor.fetchall()
        
        await cursor.close()

        return raw_data

    async def down_sample_data(self, data: list|dict, time_range: int, sleep_interval: int, start: int) -> None:
        if isinstance(data, dict):
            temp = {}
            for key in data:
                temp[key] = await self.down_sample_data(data[key], time_range, sleep_interval, start)
            return temp
        
        queue: Queue[tuple] = Queue()
        for item in data:
            queue.put(item)
        
        down_sampled_data = []
        average = []
          
        # Down sample the data to the given time range.
        try:
            current_position = start - time_range

            while True:
                item = queue.queue[0]

                if(isinstance(item[1], str)):
                    item = item[0]

                if current_position < item[1]:
                    if average == []:
                        down_sampled_data.append([item[0], current_position])
                        current_position += sleep_interval
                    else:
                        down_sampled_data.append([sum(average) / len(average), current_position])
                        average = []
                        current_position += sleep_interval
                
                elif current_position == item[1]:
                    average.append(item[0])
                    down_sampled_data.append([sum(average) / len(average), current_position])
                    average = []
                    current_position += sleep_interval
                
                elif current_position > item[1]:
                    average.append(item[0])
                    queue.get()

        except IndexError:
            pass

        return down_sampled_data   

    async def get_traffic(self, start: int, end: int, db: AioConnection) -> dict[str, int]:
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
            """, db)
            traffic[label.name] = load

        return traffic
    
    async def get_data(self, sql: str, db: AioConnection) -> int:
        cursor = await db.execute(sql)
        data: tuple = await cursor.fetchone()
        await cursor.close()

        if(data[0] == None):
            data = (0,)
        
        return data[0]
    
    async def get_cpu_usage(self, start: int, end: int, db: AioConnection) -> int:
        return await self.get_data(f"""--sql
            SELECT AVG(value) FROM resource
            WHERE resource = {Label.CPU_USAGE.value}
            AND created < {start}
            AND created >= {end}
        """, db)

    async def get_memory_usage(self, start: int, end: int, db: AioConnection) -> int:
        return await self.get_data(f"""--sql
            SELECT AVG(value) FROM resource
            WHERE resource = {Label.MEMORY_USAGE.value}
            AND created < {start}
            AND created >= {end}
        """, db)

    async def get_shell_sessions(self, start: int, end: int, db: AioConnection) -> int:
        return await self.get_data(f"""--sql
            SELECT AVG(value) FROM resource
            WHERE resource = {Label.SHELLS.value}
            AND created < {start}
            AND created >= {end}
        """, db)

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

            cursor.executescript(f"""--sql
                DELETE FROM resource where created < {CLEAR_OLD_METRICS};
                DELETE FROM metric where created < {CLEAR_OLD_METRICS};
            """)

            sleep(METRIC_INTERVAL)

def start_resource_monitor() -> None:
    try:
        monitor = ResourceMonitor()
        monitor.monitor()
    except KeyboardInterrupt:
        exit(0)