from typing import List
from multiprocessing import Queue
import sqlite3
from time import sleep
from json import loads
from uuid import uuid4
from .LogWriter import LogWriter

class Log():
    def __init__(self, messages: Queue) -> None:
        self.messages: Queue[str] = messages
        self.log_writer: LogWriter = LogWriter()

    def log(self, message: dict) -> None:
        self.log_writer.write(message)

    def run(self) -> None:
        while True:
            try:
                message: dict[str] = loads(self.messages.get(False))
                self.log(message)
                logged_messages = True
            except Exception:
                logged_messages = False

            if not logged_messages:
                sleep(0.01)


def start_logging(messages: Queue) -> None:
    try:
        log = Log(messages)
        log.run()
    except KeyboardInterrupt:
        exit(0)