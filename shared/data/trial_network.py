from enum import Enum, unique
from uuid import uuid4
from shared.data.trial_network_descriptor import EntityDescriptor
from shared import Library, Playbook
from typing import Any


class Entity:
    @unique
    class Status(Enum):
        Null, Stopped, Running, Errored = range(4)

    @unique
    class ValueType(Enum):
        Null, Default, Custom = range(3)

    def __init__(self, name: str, parent: 'TrialNetwork'):
        self.parent = parent
        self.Name = name
        self.Status = Entity.Status.Null
        self.ValueNames = list(self.Description.Parameters.keys())
        if self.Playbook is not None:
            self.ValueNames.extend(list(self.Playbook.PublicValues.keys()))


    @property
    def Description(self) -> EntityDescriptor:
        res = self.parent.Descriptor.Entities.get(self.Name)
        if res is None:
            raise RuntimeError(f"Inconsistent TN: Entity {self.Name} exists in TN but is not defined in TND")
        return res

    @property
    def Playbook(self) -> Playbook | None:
        return Library.GetPlaybook(self.Description.Type)

    @property
    def Values(self) -> {}:
        res = {}
        for name in sorted(self.ValueNames):
            res[name] = self[name]
        return res

    def __getitem__(self, item) -> (Any, ValueType):
        """First checks if the value has been customized and returns it, if that fails tries to see if there is
        a default value with that name, if not, returns None and specifies that the value is indeed 'Null'"""

        try:
            res = self.Description.Parameters[item]
            return res, Entity.ValueType.Custom
        except KeyError:
            if self.Playbook is not None:
                try:
                    res = self.Playbook.PublicValues[item]
                    return res, Entity.ValueType.Default
                except KeyError: pass
        return None, Entity.ValueType.Null


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
            for name, description in self.Descriptor.Entities.items():
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
