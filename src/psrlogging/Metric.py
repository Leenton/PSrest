from enum import Enum
from typing import List, Tuple

class MetricLabel(Enum):
    REQUEST = 'Request'
    INVALID_CREDENTIALS = 'Invalid Credentials Error'
    UNAUTHORISED = 'Unauthorised Error'

class Metric(object):
    def __init__(self, *labels: MetricLabel) -> None:
        self.labels = []

        if isinstance(labels, tuple):
            for label in labels:
                self.labels.append(str(label))

        else:
            self.labels.append(str(labels))

    def get_labels(self) -> List[str]:
        return self.labels
