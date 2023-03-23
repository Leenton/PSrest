import asyncio
import nats # pip install nats.py
from datetime import datetime
from time import sleep

async def main():
    # Connect to NATS!
    

    # Simple publisher and async subscriber via coroutine.
    nc = await nats.connect("localhost:4222")
    
    while(True):
        await nc.publish("test", b'Hello')
        print("Sent")

    
    # msg = await sub.next_msg(60)
    # now = datetime.now()
    # count = 0
    
    # while(True):
    #     msg = await sub.next_msg(5)
    #     print("Received:", msg.data)
    #     count += 1
    #     if(count == 1000):
    #         break

    # print(now)
    # print(datetime.now())
        

if __name__ == '__main__':
    asyncio.run(main())
