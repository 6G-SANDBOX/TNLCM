import tempfile
import os
import yaml
import json

from base64 import b64decode
from shared import Library
from shared.data import TrialNetwork, Entity
from core.Transition.jenkins_handler import JenkinsHandler
from .base_handler import BaseHandler
from time import sleep

class ToStarted(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToStarted", trialNetwork)

    def Run(self):

        order = list(self.tn.Descriptor.DeploymentOrder)
        library = Library()
        jenkins_handler = JenkinsHandler()

        # Check if the report file was created
        path_report_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', 'report.md')
        if os.path.isfile(path_report_file):
            os.remove(path_report_file)

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
            jenkins_client = jenkins_handler.get_jenkins_client()
            job_name = jenkins_handler.get_job_name()
            tn_id = os.getenv("JENKINS_TN_ID")
            component_settings = library.GetComponent(entity_name)
            component_library_branch = component_settings.Branch
            path_temp_file = self._create_temp_file(entity, tn_id)
            sleep(1)
            if os.path.isfile(path_temp_file):
                with open(path_temp_file, 'rb') as temp_file:
                    parameters = {
                        "TN_ID": tn_id,
                        "LIBRARY_COMPONENT_NAME": entity_name,
                        "LIBRARY_BRANCH": component_library_branch,
                        "DEPLOYMENT_SITE": os.getenv("JENKINS_DEPLOYMENT_SITE"),
                    }
                    job_url = jenkins_client.build_job_url(name=job_name, parameters=parameters)
                    file = {"FILE": (path_temp_file, temp_file)}
                    response = jenkins_handler.deploy_component(job_url=job_url, file=file)
                    if response.status_code == 201:
                        # job_info = server.get_job_info(name=job_name)
                        last_build_number = jenkins_client.get_job_info(name=job_name)["nextBuildNumber"]
                        while last_build_number != jenkins_client.get_job_info(name=job_name)["lastCompletedBuild"]["number"]:
                            sleep(15)

                        if jenkins_client.get_job_info(name=job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                            sleep(15)
                            path_jenkins_response_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', 'jenkins_response.json')
                            rename_jenkins_response_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', str(entity_name) + "_" + str(tn_id) + '.json')
                            if os.path.isfile(path_jenkins_response_file):
                                os.rename(path_jenkins_response_file, rename_jenkins_response_file)
                                with open(rename_jenkins_response_file, 'r') as jenkins_response:
                                    jenkins_data = json.load(jenkins_response)
                                    result_msg_encode = jenkins_data.get('result_msg')
                                    result_msg_decode = b64decode(result_msg_encode).decode('utf-8')

                                    with open(path_report_file, 'a') as report:
                                        report.write(result_msg_decode + '\n')
                            else:
                                print(f"File {path_jenkins_response_file} not found.")
                        else:
                            print("Error. Pipeline failed.")
                    else:
                        print(f"Error. Bad request.")
            else:
                print(f"File {path_temp_file} not found.")

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
                callback_directory_vxlan = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', "tn_vxlan" + "_" + str(tn_id) + '.json')
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