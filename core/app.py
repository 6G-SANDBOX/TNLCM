import sys
sys.path.append('..')

import time
from shared import Log, Child
from shared.data import TrialNetwork
from Transition import ToStarted, ToDestroyed, TransitionHandler
from yaml import safe_load

from flask import Flask
from flask_cors import CORS

from Testbed import Testbed
from Library import Library

Log.Initialize(outFolder='.', logName='Core', consoleLevel='DEBUG', fileLevel='DEBUG', app=None)
Library.Initialize()

testbed: [TrialNetwork] = []


def addTn():
    with open("../sample_descriptor.yml", 'r', encoding='utf-8') as file:
        descriptor = safe_load(file)
    tn = TrialNetwork(descriptor)
    Testbed.AddTrialNetwork(tn)
    return tn


class Scheduler(Child):
    def Run(self):
        while True:
            Log.I(f"Testbed -> {Testbed.ListTrialNetworks()}")
            for id in Testbed.ListTrialNetworks():
                tn = Testbed.GetTrialNetwork(id)
                match tn.Status:
                    case TrialNetwork.Status.Transitioning:
                        if tn.Handler is None:
                            Log.I(f"Handling {tn.Id}")
                            TransitionHandler.Handle(tn)
                        else:
                            Log.I(f"{tn.Id} already served")
                    case TrialNetwork.Status.Destroyed:
                        Log.I(f'Deleting {tn.Id}')
                        Testbed.RemoveTrialNetwork(tn.Id)
            time.sleep(5)


scheduler = Scheduler("scheduler")
scheduler.Start()

from flask_restx import Api
from Api import trial_network_api
from Api import testbed_api
from Api import playbook_api

app = Flask(__name__)
CORS(app)

api = Api(
    version='0.1'
)

api.add_namespace(trial_network_api, path="/trial_network")
api.add_namespace(testbed_api, path="/testbed")
api.add_namespace(playbook_api, path="/playbook")
api.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
