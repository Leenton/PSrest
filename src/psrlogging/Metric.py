from enum import Enum
from typing import List, Tuple
class MetricLabel(Enum):
    REQUEST = 1
    INVALID_CREDENTIALS = 2
    UNAUTHORISED = 3

class Metric(object):
    def __init__(self, *labels: MetricLabel) -> None:
        self.labels = labels

    def get_labels(self) -> Tuple[MetricLabel]:
        return self.labels
