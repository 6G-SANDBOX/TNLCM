from shared import Child, Level
from shared.data import TrialNetwork, Entity
from .base_handler import BaseHandler
from core.Tasks import SSH
from shared import Library
from requests import post
from jenkins import Jenkins

import os
import yaml

class ToStarted(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToStarted", trialNetwork)

    def Run(self):
        from time import sleep

        order = list(self.tn.Descriptor.DeploymentOrder)

        for name in order:
            entity = self.tn.Entities[name]
            if entity.Playbook is not None:
                print(f"Instantiating '{entity.Name}' - Playbook: '{entity.Playbook.SnapshotMetadata.Commit}'")
                print(f"  Values: {entity.Values}")
                for step in entity.Playbook.Flow['Install']:
                    print(f"    {step}")
            else:
                print(f"Unable to instantiate '{entity.Name}': Unknown type '{entity.Description.Type}'")
            sleep(1)

            # Connecting to the jenkins server using python-jenkins API
            jenkins_client = Jenkins(os.getenv("JENKINS_SERVER"), username=os.getenv("JENKINS_USER"), password=os.getenv("JENKINS_PASSWORD"))
            job_name = "02_Trial_Network_Component"
            route_file = None
            if name == "VXLAN":
                route_file = os.path.join("..", "..", "TNLCM", "DEMO", "file_vxlan.yaml")
            elif name == "BASTION":
                route_file = os.path.join("..", "..", "TNLCM", "DEMO", "file_bastion.yaml")
            else:
                print("Error")
            if route_file is not None:
                file_path = os.path.abspath(route_file)
                with open(file_path, "rb") as file:
                    content = yaml.safe_load(file)
                    tn_id = content.get("tn_id")
                    component_name = content.get("component_name")
                    parameters = {
                        "TN_ID": tn_id,
                        "LIBRARY_COMPONENT_NAME": component_name,
                        "LIBRARY_BRANCH": "first_tn_demo",
                        "DEPLOYMENT_SITE": "uma",
                    }
                    job_url = jenkins_client.build_job_url(name=job_name, parameters=parameters)
                    file.seek(0)
                    files = {"FILE": (file_path, file)}
                    response = post(job_url, auth=(os.getenv("JENKINS_USER"), os.getenv("JENKINS_TOKEN")), files=files)

                if response.status_code == 201:
                    # job_info = server.get_job_info(name=job_name)
                    last_build_number = jenkins_client.get_job_info(name=job_name)["nextBuildNumber"]
                    while last_build_number != jenkins_client.get_job_info(name=job_name)["lastCompletedBuild"]["number"]:
                        sleep(10)

                    if jenkins_client.get_job_info(name=job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                        print("Work")
                        sleep(15)
                        callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback')
                        callback_response_jenkins = str(tn_id) + '.json'
                        callback_full_route = os.path.join(callback_directory, callback_response_jenkins)
                        if os.path.isfile(callback_full_route):
                            print("File found")
                        else:
                            print("File not found")
                    else:
                        print("Error")
                else:
                    print("Error")

            entity.Status = Entity.Status.Running

        self.tn.CompleteTransition()