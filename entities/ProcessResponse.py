import asyncio

class ProcessResponse():
    def __init__(self, status: int, length: bytes, reader: asyncio.StreamReader = None, writer: asyncio.StreamWriter = None) -> None:
        self.status = status
        self.length = length
        self.reader = reader
        self.writer = writer