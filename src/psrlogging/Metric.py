from enum import Enum
from typing import List, Tuple

class MetricLabel(Enum):
    REQUEST = 1
    INVALID_CREDENTIALS_ERROR = 2
    UNAUTHORISED_ERROR = 3
    BAD_REQUEST_ERROR = 4   
    UNEXPECTED_ERROR = 5


class Metric(object):
    def __init__(self, *labels: MetricLabel) -> None:
        self.labels: List[str] = []

        for label in labels:
            self.labels.append(label.value)

    def get_labels(self) -> List[str]:
        return self.labels
    
    def serialise(self):
        return {
            'labels': self.labels
        }

