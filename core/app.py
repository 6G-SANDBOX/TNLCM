import time
from shared import Log, Child
from shared.data import TrialNetwork
from Transition import ToStarted, ToDestroyed, TransitionHandler
import cson
from yaml import safe_load

from Composer import Composer


Log.Initialize(outFolder='.', logName='Core', consoleLevel='DEBUG', fileLevel='DEBUG', app=None)

testbed: [TrialNetwork] = []


def addTn():
    with open("../sample_descriptor.yml", 'r', encoding='utf-8') as file:
        descriptor = safe_load(file)
    tn = TrialNetwork(descriptor)
    testbed.append(tn)
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


experimenter = Experimenter("experimenter")
experimenter.Start()

while True:
    Log.I(f"Testbed -> {[(q.Id, q.Status.name, q.Transition) for q in testbed]}")
    for tn in testbed:
        match tn.Status:
            case TrialNetwork.Status.Transitioning:
                if tn.Handler is None:
                    Log.I(f"Handling {tn.Id}")
                    TransitionHandler.Handle(tn)
                else:
                    Log.I(f"{tn.Id} already served")
            case TrialNetwork.Status.Destroyed:
                Log.I(f'Deleting {tn.Id}')
                _ = testbed.remove(tn)
    time.sleep(5)
