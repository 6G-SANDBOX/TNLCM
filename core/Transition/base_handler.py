from shared import Child, Level
from shared.data import TrialNetwork
from datetime import datetime
from os.path import join


class BaseHandler(Child):
    def __init__(self, name: str, trialNetwork: TrialNetwork):
        self.tn = trialNetwork
        super().__init__(name=f'{datetime.utcnow().timestamp()}_{name}', logFolder=trialNetwork.LogFolder)


