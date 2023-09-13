from shared.data import TrialNetwork
from uuid import UUID


class Testbed:
    TrialNetworks = {}

    @classmethod
    def AddTrialNetwork(cls, tn: TrialNetwork):
        cls.TrialNetworks[tn.Id] = tn

    @classmethod
    def CreateAndAddTrialNetwork(cls, descriptor: {}) -> TrialNetwork:
        tn = TrialNetwork(descriptor)
        cls.AddTrialNetwork(tn)
        return tn

    @classmethod
    def RemoveTrialNetwork(cls, id: str):
        _ = cls.TrialNetworks.pop(id)

    @classmethod
    def ListTrialNetworks(cls):
        res = list(cls.TrialNetworks.keys())
        return res

    @classmethod
    def GetTrialNetwork(cls, id: str | UUID):
        if isinstance(id, UUID):
            id = str(id)

        return cls.TrialNetworks.get(id, None)

