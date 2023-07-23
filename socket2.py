import PSRestQueue
import asyncio

queue = PSRestQueue.PSRestQueue()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(queue.start())

