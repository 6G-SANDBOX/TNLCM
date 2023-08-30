from shared import Child, Level
from shared.data import TrialNetwork
from .base_handler import BaseHandler
from core.Tasks import SSH


class ToDestroyed(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToDestroyed", trialNetwork)

    def Run(self):
        from time import sleep

        order = reversed(list(self.tn.Descriptor.DeploymentOrder))

        for name in order:
            entity = self.tn.Entities[name]
            print(f"Decommissioning {entity.Name}")
            sleep(1)

        self.tn.CompleteTransition()


