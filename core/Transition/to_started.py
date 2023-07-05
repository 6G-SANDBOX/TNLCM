from shared import Child, TrialNetwork, Status, Level
from .base_handler import BaseHandler
from core.Tasks import SSH


class ToStarted(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToStarted", trialNetwork)

    def Run(self):
        tasks = self.tn.Descriptor["Actions"]["OnStart"]

        self.Log(Level.INFO, f"Tasks to run: {tasks}")

        for task in tasks:
            if task['Type'] == "SSH":
                SSH(self.tn, task).Start()

        self.tn.CompleteTransition()

