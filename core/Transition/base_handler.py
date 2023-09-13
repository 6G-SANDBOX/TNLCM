from shared import Child, Level
from shared.data import TrialNetwork
from datetime import datetime


class BaseHandler(Child):
    def __init__(self, name: str, trialNetwork: TrialNetwork):
        self.tn = trialNetwork
        super().__init__(name=f'{self.tn.Id}_{name}_{datetime.utcnow().timestamp()}')


