from enum import Enum

class SnapshotState(Enum):
    IDLE = 0
    REQUESTING = 1
    GENERATING = 2
    COMPLETED = 3
    FAILED = 4
    
class SnapshotInterupter():
    def __init__(self):
        self.state = SnapshotState.IDLE 

    def request(self):
        self.state = SnapshotState.REQUESTING