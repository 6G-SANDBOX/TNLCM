from shared import Child, Level
from shared.data import TrialNetwork
from .base_handler import BaseHandler
from core.Tasks import SSH
from shared import Library


class ToStarted(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToStarted", trialNetwork)

    def Run(self):
        from time import sleep

        order = list(self.tn.Descriptor.DeploymentOrder)

        for name in order:
            entity = self.tn.Entities[name]
            playbook = Library.GetPlaybook(entity.Description.Type)  # TODO: Probably handle inside the entity instead
            print(f"Instantiating {entity.Name} - Playbook: '{playbook}'")
            sleep(1)

        self.tn.CompleteTransition()

