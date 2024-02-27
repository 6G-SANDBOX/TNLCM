import tempfile
import os
import yaml
import json

from base64 import b64decode
from shared import Child, Level
from shared.data import TrialNetwork, Entity
from .base_handler import BaseHandler
from core.Tasks import SSH
from shared import Library
from requests import post
from jenkins import Jenkins
from time import sleep

class ToStarted(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToStarted", trialNetwork)

    def Run(self):

        order = list(self.tn.Descriptor.DeploymentOrder)

        # Check if the report file was created
        report_callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', 'report.md')
        if os.path.isfile(report_callback_directory):
            os.remove(report_callback_directory)

        for o in order:
            entity_name = o.Name
            entity = self.tn.Entities[entity_name]
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
            tn_id = os.getenv("JENKINS_TN_ID")
            path_temp_file = self._create_temp_file(entity, tn_id)
            sleep(1)
            if os.path.isfile(path_temp_file):
                with open(path_temp_file, 'rb') as file:
                    parameters = {
                        "TN_ID": tn_id,
                        "LIBRARY_COMPONENT_NAME": entity_name,
                        "LIBRARY_BRANCH": os.getenv("JENKINS_6GLIBRARY_BRANCH"),
                        "DEPLOYMENT_SITE": os.getenv("JENKINS_DEPLOYMENT_SITE"),
                    }
                    job_url = jenkins_client.build_job_url(name=job_name, parameters=parameters)
                    files = {"FILE": (path_temp_file, file)}
                    response = post(job_url, auth=(os.getenv("JENKINS_USER"), os.getenv("JENKINS_TOKEN")), files=files)

                    if response.status_code == 201:
                        # job_info = server.get_job_info(name=job_name)
                        last_build_number = jenkins_client.get_job_info(name=job_name)["nextBuildNumber"]
                        while last_build_number != jenkins_client.get_job_info(name=job_name)["lastCompletedBuild"]["number"]:
                            sleep(15)

                        if jenkins_client.get_job_info(name=job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                            sleep(15)
                            callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', 'jenkins_response.json')
                            new_callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', str(entity_name) + str(tn_id) + '.json')
                            os.rename(callback_directory, new_callback_directory)
                            if os.path.isfile(new_callback_directory):
                                with open(new_callback_directory, 'r') as jenkins_response:
                                    jenkins_data = json.load(jenkins_response)
                                    result_msg_encode = jenkins_data.get('result_msg')
                                    result_msg_decode = b64decode(result_msg_encode).decode('utf-8')

                                    with open(report_callback_directory, 'a') as report:
                                        report.write(result_msg_decode + '\n')
                            else:
                                print(f'File {new_callback_directory} not found.')
                        else:
                            print("Error. Pipeline failed.")
                    else:
                        print("Error. Bad request.")
            else:
                print(f'File {new_callback_directory} not found.')

            entity.Status = Entity.Status.Running

        self.tn.CompleteTransition()

    def _create_temp_file(self, entity, tn_id):
        with tempfile.NamedTemporaryFile(delete=False, dir=self.TempFolder, suffix=".yaml", mode='w') as tempFile:
            public = entity.Description.Public or {}
            data = {
                'tnlcm_callback': os.getenv("CALLBACK_URL") + "/callback",
                **public
            }
            entity_name = entity.Description.Name
            if entity_name == "tn_bastion" or entity_name == "vm_kvm_very_small":
                callback_directory_vxlan = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', "tn_vxlan" + str(tn_id) + '.json')
                if os.path.isfile(callback_directory_vxlan):
                    with open(callback_directory_vxlan, 'r') as file:
                        json_data = json.load(file)
                        tn_vxlan_id = json_data.get('tn_vxlan_id')
                        data["one_component_networks"] = [0, int(tn_vxlan_id)]
                        if entity_name == "tn_bastion":
                            data["one_bastion_wireguard_allowed_networks"] = "192.168.199.0/24"
                else:
                    print(f'File {callback_directory_vxlan} not found.')
            yaml.dump(data, tempFile, default_flow_style=False)
            return tempFile.name