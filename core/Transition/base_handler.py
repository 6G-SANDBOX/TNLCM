from shared import Child, TrialNetwork, Status, Level
from datetime import datetime


class BaseHandler(Child):
    def __init__(self, name: str, trialNetwork: TrialNetwork):
        self.tn = trialNetwork
        super().__init__(name=f'{self.tn.Id}_{name}_{datetime.utcnow().timestamp()}')


