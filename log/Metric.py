from enum import Enum
from datetime import datetime

class Label(Enum):
    REQUEST = 1
    INVALID_CREDENTIALS_ERROR = 2
    UNAUTHORISED_ERROR = 3
    BAD_REQUEST_ERROR = 4   
    UNEXPECTED_ERROR = 5
    CPU_USAGE = 6
    MEMORY_USAGE = 7
    SHELLS = 8
    DROPPED_REQUEST = 9


class Metric(object):
    def __init__(self, *labels: Label) -> None:
        self.created = int(datetime.timestamp(datetime.now()))
        self.labels = []

        for label in labels:
            self.labels.append(label.value)
    
    def serialise(self):
        return {
            'labels': self.labels,
            'created': self.created
        }

