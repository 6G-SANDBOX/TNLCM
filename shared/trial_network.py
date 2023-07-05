from enum import Enum, unique
from uuid import uuid4


@unique
class Status(Enum):
    Null, Transitioning, Started, Destroyed = range(4)


class TrialNetwork:
    def __init__(self, descriptor: dict):
        self.Id = str(uuid4())
        self.Descriptor = descriptor
        self.Status = Status.Null
        self.Transition = (None, None)
        self.Handler = None

    def MarkForTransition(self, toStatus: Status) -> bool:
        if self.Status != Status.Transitioning:
            self.Transition = (self.Status, toStatus)
            self.Status = Status.Transitioning
            return True
        return False

    def CompleteTransition(self):
        self.Handler = None
        self.Status = self.Transition[1]
        self.Transition = (None, None)
