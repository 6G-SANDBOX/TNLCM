import sys
sys.path.append('..')


import time
from shared import Log, Child
from shared.data import TrialNetwork
from Transition import ToStarted, ToDestroyed, TransitionHandler
import cson
from yaml import safe_load

from flask import Flask

from Testbed import Testbed

Log.Initialize(outFolder='.', logName='Core', consoleLevel='DEBUG', fileLevel='DEBUG', app=None)

testbed: [TrialNetwork] = []


def addTn():
    with open("../sample_descriptor.yml", 'r', encoding='utf-8') as file:
        descriptor = safe_load(file)
    tn = TrialNetwork(descriptor)
    Testbed.AddTrialNetwork(tn)
    return tn


class Experimenter(Child):
    def Run(self):
        time.sleep(3)
        print("ADD")
        tn = addTn()
        time.sleep(5)
        print("START")
        tn.MarkForTransition(TrialNetwork.Status.Started)

        goOn = True
        while goOn:
            time.sleep(2)
            goOn = not tn.MarkForTransition(TrialNetwork.Status.Destroyed)
            if goOn:
                print("BUSY")
            else:
                print("DELETE")


class Scheduler(Child):
    def Run(self):
        while True:
            Log.I(f"Testbed -> {[(q.Id, q.Status.name, q.Transition) for q in testbed]}")
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
                        # Testbed.RemoveTrialNetwork(tn.Id)
            time.sleep(5)


experimenter = Experimenter("experimenter")
experimenter.Start()

scheduler = Scheduler("scheduler")
scheduler.Start()

from flask_restx import Api
from Api import trial_network_api
from Api import testbed_api
app = Flask(__name__)

api = Api(
    version='0.1'
)

api.add_namespace(trial_network_api, path="/trial_network")
api.add_namespace(testbed_api, path="/testbed")
api.init_app(app)

if __name__ == "__main__":
    app.run()
