from enum import Enum, unique
from uuid import uuid4
from shared.data.trial_network_descriptor import EntityDescriptor

class Entity:
    @unique
    class Status(Enum):
        Nope, Transitioning, Started, Destroyed = range(4)

    def __init__(self, name: str, parent: 'TrialNetwork'):
        self.parent = parent
        self.Name = name
        self.Status = Entity.Status.Nope

    @property
    def Description(self) -> EntityDescriptor:
        res = self.parent.Descriptor.Entities.get(self.Name)
        if res is None:
            raise RuntimeError(f"Inconsistent TN: Entity {self.Name} exists in TN but is not defined in TND")
        return res


class TrialNetwork:
    @unique
    class Status(Enum):
        Null, Transitioning, Started, Destroyed = range(4)

    def __init__(self, descriptor: dict):
        from core.Composer import Composer

        self.Id = str(uuid4())
        self.Descriptor = descriptor
        self.Status = TrialNetwork.Status.Null
        self.Transition = (None, None)
        self.Handler = None

        self.Descriptor = Composer.Compose(descriptor)
        self.Valid = self.Descriptor.Valid
        self.Entities = {}

        if self.Valid:
            for name in self.Descriptor.Entities:
                self.Entities[name] = Entity(name, self)

    def MarkForTransition(self, toStatus: Status) -> bool:
        if self.Status != TrialNetwork.Status.Transitioning:
            self.Transition = (self.Status, toStatus)
            self.Status = TrialNetwork.Status.Transitioning
            return True
        return False

    def CompleteTransition(self):
        self.Handler = None
        self.Status = self.Transition[1]
        self.Transition = (None, None)
