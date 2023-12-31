from json import dumps
import asyncio
from queue import Queue
from uuid import uuid4
from configuration import (
    FAILED,
    PS_PROCESSORS,
    MAX_PROCESSES,
    PROCESSOR_SPIN_UP_PERIOD,
    PROCESSOR_SPIN_DOWN_PERIOD
)
from entities import (
    Schedule,
    Ticket,
    Process,
    ProcessStatus,
    ProcessResponse,
    Clock
)
from .SnapshotInterupter import *

class ControlUnit():
    def __init__(
            self,
            schedule: Schedule,
            processes:dict[str, Process],
            snapshot_buffer: asyncio.Queue[bytes],
            clock: Clock,
            responses: dict[str, ProcessResponse],
            ticket_queue: Queue[Ticket],
            accumulator: asyncio.Queue[Ticket],
            snapshot_interupter: SnapshotInterupter
        ) -> None:
        self.schedule: Schedule = schedule
        self.clock: Clock = clock
        self.aceepting_requests = True
        self.snapshot_interupter: SnapshotInterupter = snapshot_interupter
        self.snapshots: list[dict] = []
        self.snapshot_buffer: asyncio.Queue[bytes] = snapshot_buffer
        self.processes: dict[str, Process] = processes
        self.responses: dict[str, ProcessResponse] = responses
        self.ticket_queue: Queue[Ticket] = ticket_queue
        self.accumulator: asyncio.Queue[Ticket] = accumulator
        self.oldest_free_process: str = ''

    def kill_process(self, pid: str):
        process = self.processes.pop(pid)
        process.terminate()

    def spawn_process(self):
        pid = uuid4().hex
        self.processes[pid] = Process(pid, self.clock.now, self.clock.now)
        
    def filter_schedule(self) -> list[dict]:
        def peek(ticket: Ticket|None) -> Ticket|None:
            self.snapshots.append(ticket.serialise())
            return ticket

        if(self.snapshot_interupter.state == SnapshotState.REQUESTING):
            self.snapshots = []
            self.schedule.filter(
                lambda ticket: ticket if ticket.expiry > self.clock.now else None,
                peek
            )
            self.snapshot_interupter.state = SnapshotState.GENERATING

        else:
            self.schedule.filter(
                lambda ticket: ticket if ticket.expiry > self.clock.now else None
            )

    def schedule_from_queue(self):
        empty = self.ticket_queue.qsize() == 0

        if(self.aceepting_requests and not empty):
            self.schedule.add(self.ticket_queue.get())

        elif(not empty):
            self.responses[self.ticket_queue.get().id] = ProcessResponse(FAILED, 0)
        
    async def execute_from_schedule(self)-> None:
        # Itterate over the dictionary of processes
        oldest_free_process: float | None = None

        for pid, process in self.processes.items():
            if(process.current_ticket and process.current_ticket.expiry < self.clock.now):
                self.kill_process(pid)

            elif(process.status == ProcessStatus.FREE):
                if(self.schedule.peek()):
                    await self.accumulator.put(self.schedule.get())

                if(not oldest_free_process):
                    oldest_free_process = pid
                else:
                    if(self.processes[pid].status == ProcessStatus.FREE and process.last_seen < self.processes[oldest_free_process].last_seen):
                        oldest_free_process = pid
                        
            elif(process.status == ProcessStatus.BUSY and self.snapshot_interupter.state == SnapshotState.GENERATING):
                self.snapshots.append(process.current_ticket.serialise())
        
        if(self.snapshot_interupter.state == SnapshotState.GENERATING):
            self.snapshot_interupter.state = SnapshotState.COMPLETED
            await self.snapshot_buffer.put(dumps(self.snapshots).encode('utf-8'))
            self.snapshots = []

    async def scale_processes_up(self) -> bool:
        if(len(self.processes) < PS_PROCESSORS):
            self.spawn_process()
            return True
        
        if(len(self.processes) < MAX_PROCESSES):
            ticket = self.schedule.peek()

            if(ticket and ticket.created < self.clock.now - PROCESSOR_SPIN_UP_PERIOD):
                self.spawn_process()
                return True

        return False
        
    def scale_processes_down(self):
        if(len(self.processes) > PS_PROCESSORS):
            if(self.oldest_free_process and self.processes[self.oldest_free_process].last_seen < self.clock.now - PROCESSOR_SPIN_DOWN_PERIOD ):
                self.kill_process(self.oldest_free_process)

    async def start(self):
        while len(self.processes) < PS_PROCESSORS:
            self.spawn_process()

        while True:
            self.filter_schedule()
            self.schedule_from_queue()
            await self.execute_from_schedule() # Execute the commands in the schedule

            if(not await self.scale_processes_up()):
                self.scale_processes_down()

            await self.clock.tick()