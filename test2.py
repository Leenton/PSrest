import asyncio
import nats

async def main():
    # Connect to NATS!
    nc = await nats.connect("localhost:4222")

    # Receive messages on 'foo'
    sub = await nc.subscribe("test")

    # Process a message
    msg = await sub.next_msg(60)
    print("Received:", msg)

if __name__ == '__main__':
    asyncio.run(main())