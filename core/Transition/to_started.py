from shared import Child, Level
from shared.data import TrialNetwork, Entity
from .base_handler import BaseHandler
from core.Tasks import SSH
from shared import Library
from requests import post
from jenkins import Jenkins

import os

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

            server = Jenkins(os.getenv("JENKINS_SERVER"), username=os.getenv("JENKINS_USER"), password=os.getenv("JENKINS_PASSWORD"))
            job_name = "02_Trial_Network_Component"
            route_file = os.path.join("..", "..", "TNLCM", "DEMO", "file_vxlan.yaml")
            file_path = os.path.abspath(route_file)
            parameters = {
                "TN_ID": "ABCDEF",
                "LIBRARY_COMPONENT_NAME": "tn_vxlan",
                "LIBRARY_BRANCH": "first_tn_demo",
                "DEPLOYMENT_SITE": "uma",
            }
            job_url = server.build_job_url(name=job_name, parameters=parameters)
            with open(file_path, "rb") as file:
                files = {"FILE": (file_path, file)}
                response = post(job_url, auth=(os.getenv("JENKINS_USER"), os.getenv("JENKINS_TOKEN")), files=files)

            if response.status_code == 201:
                # job_info = server.get_job_info(name=job_name)
                last_build_number = server.get_job_info(name=job_name)["nextBuildNumber"]
                while last_build_number != server.get_job_info(name=job_name)["lastCompletedBuild"]["number"]:
                    pass

                if server.get_job_info(name=job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                    print("Work")
                else:
                    print("Error")
            else:
                print("Error")
            # TODO: 4 retrieve the values generated during the pipeline:
            # - Either parse the logs (not so easily scalable)
            # - Use the callback endpoint (if/when available) to retrieve all values as a dictionary

            entity.Status = Entity.Status.Running

        self.tn.CompleteTransition()

