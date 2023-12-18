from datetime import datetime
from asyncio import sleep

class Clock():
    def __init__(self) -> None:
        self.now: float = datetime.timestamp(datetime.now())

    async def tick(self) -> float:
        await sleep(0.001)
        self.now = datetime.timestamp(datetime.now())