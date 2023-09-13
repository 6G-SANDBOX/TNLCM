from shared.data import TrialNetworkDescriptor, EntityDescriptor


class Composer:
    @classmethod
    def Compose(cls, rawDescriptor: {}) -> TrialNetworkDescriptor:
        res = TrialNetworkDescriptor(rawDescriptor)

        return res