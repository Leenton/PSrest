import asyncio
import nats # pip install nats.py
from datetime import datetime
from time import sleep

async def main():
    nc = await nats.connect()

    future = asyncio.Future()

    async def cb(msg):
        nonlocal future
        future.set_result(msg)

    await nc.subscribe("test", queue="test", cb=cb)
    
    while(True):

        msg = await asyncio.wait_for(future, 10)
        print(msg.data)

if __name__ == '__main__':
    asyncio.run(main())