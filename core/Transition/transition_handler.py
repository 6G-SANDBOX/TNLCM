from shared import TrialNetwork, Status
from .to_started import ToStarted
from .to_destroyed import ToDestroyed


class TransitionHandler:
    @classmethod
    def Handle(cls, tn: TrialNetwork):
        f, t = tn.Transition
        match t:
            case Status.Started:
                handler = ToStarted(tn)
            case Status.Destroyed:
                handler = ToDestroyed(tn)
            case _:
                handler = None

        tn.Handler = handler
        handler.Start()
