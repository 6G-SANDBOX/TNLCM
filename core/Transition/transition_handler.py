from shared.data import TrialNetwork
from .to_started import ToStarted
from .to_destroyed import ToDestroyed


class TransitionHandler:
    @classmethod
    def Handle(cls, tn: TrialNetwork):
        f, t = tn.Transition
        match t:
            case TrialNetwork.Status.Started:
                handler = ToStarted(tn)
            case TrialNetwork.Status.Destroyed:
                handler = ToDestroyed(tn)
            case _:
                handler = None

        tn.Handler = handler
        handler.Start()
