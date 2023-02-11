import asyncio
import nats
from datetime import datetime

async def main():
    # Connect to NATS!
    nc = await nats.connect("localhost:4222")

    # Receive messages on 'foo'
    sub = await nc.subscribe("test")

    
    msg = await sub.next_msg(60)
    now = datetime.now()
    count = 0
    
    while(True):
        msg = await sub.next_msg(60)
        print("Received:", msg)
        count += 1
        if(count == 1000):
            break

    print(now)
    print(datetime.now())
        

if __name__ == '__main__':
    asyncio.run(main())
