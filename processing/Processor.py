from queue import Queue
import asyncio
from entities import Clock, Process, ProcessResponse, Ticket, Schedule
from .IORouter import IORouter
from .ControlUnit import ControlUnit
from .SnapshotInterupter import *
class Processor():
    def __init__(self):
        self.queue: Queue[Ticket] = Queue()
        self.processes: dict[str, Process] = {}
        self.responses: dict[str, ProcessResponse]  = {}
        self.schedule: Schedule = Schedule()
        self.accumulator: asyncio.Queue[Ticket] = asyncio.Queue()
        self.snapshot_buffer: asyncio.Queue[bytes] = asyncio.Queue()
        self.clock: Clock = Clock()
        self.ticket_queue: Queue[Ticket] = Queue()
        self.snapshot_interupter = SnapshotInterupter()

    async def start(self):
        control_unit = ControlUnit(
            self.schedule,
            self.processes,
            self.snapshot_buffer,
            self.clock,
            self.responses,
            self.ticket_queue,
            self.accumulator,
            self.snapshot_interupter
        )
        input_router = IORouter(
            self.processes,
            self.responses,
            self.snapshot_buffer,
            self.clock,
            self.ticket_queue,
            self.accumulator,
            self.snapshot_interupter
        )
        
        route = asyncio.create_task(input_router.route())
        control = asyncio.create_task(control_unit.start())
        await route
        await control

def start_processor():
    try:
        processor = Processor()
        asyncio.run(processor.start())

    except KeyboardInterrupt:
        exit(0)
