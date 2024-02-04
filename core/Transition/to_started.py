import tempfile

from shared import Child, Level
from shared.data import TrialNetwork, Entity
from .base_handler import BaseHandler
from core.Tasks import SSH
from shared import Library
from requests import post
from jenkins import Jenkins

import os
import yaml
import json

class ToStarted(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToStarted", trialNetwork)

    def Run(self):
        from time import sleep

        order = list(self.tn.Descriptor.DeploymentOrder)

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
            tn_id = "CARLOS"
            path_temp_file = self._create_temp_file(entity, tn_id)
            sleep(1)
            try:
                with open(path_temp_file, 'rb') as file:
                    parameters = {
                        "TN_ID": tn_id,
                        "LIBRARY_COMPONENT_NAME": entity_name,
                        "LIBRARY_BRANCH": "update_bastion",
                        "DEPLOYMENT_SITE": "uma",
                    }
                    job_url = jenkins_client.build_job_url(name=job_name, parameters=parameters)
                    files = {"FILE": (path_temp_file, file)}
                    response = post(job_url, auth=(os.getenv("JENKINS_USER"), os.getenv("JENKINS_TOKEN")), files=files)

                    if response.status_code == 201:
                        # job_info = server.get_job_info(name=job_name)
                        last_build_number = jenkins_client.get_job_info(name=job_name)["nextBuildNumber"]
                        while last_build_number != jenkins_client.get_job_info(name=job_name)["lastCompletedBuild"]["number"]:
                            sleep(10)

                        if jenkins_client.get_job_info(name=job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                            print("Work")
                            sleep(15)
                            callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', 'data.json')
                            new_callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback', str(entity_name) + str(tn_id) + '.json')
                            os.rename(callback_directory, new_callback_directory)
                            if os.path.isfile(new_callback_directory):
                                # Decode content
                                print("File found")
                            else:
                                print("File not found")
                        else:
                            print("Error")
                    else:
                        print("Error")
            except FileNotFoundError:
                print(f'File {path_temp_file} not found.')
            except json.JSONDecodeError:
                print(f'Error decoding JSON in the file {path_temp_file}.')
            except Exception as e:
                print(f'Error: {str(e)}')

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
                try:
                    with open(callback_directory_vxlan, 'r') as file:
                        json_data = json.load(file)
                        tn_vxlan_id = json_data.get('tn_vxlan_id')
                        data["one_component_networks"] = [0, int(tn_vxlan_id)]
                        if entity_name == "tn_bastion":
                            data["one_bastion_wireguard_allowed_networks"] = "192.168.199.0/24"
                except FileNotFoundError:
                    print(f'File {callback_directory_vxlan} not found.')
                except json.JSONDecodeError:
                    print(f'Error decoding JSON in the file {callback_directory_vxlan}.')
                except Exception as e:
                    print(f'Error: {str(e)}')
            yaml.dump(data, tempFile, default_flow_style=False)
            return tempFile.name