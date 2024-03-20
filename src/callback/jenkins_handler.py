import os

from jenkins import Jenkins, JenkinsException
from requests import post
from json import load, dump
from base64 import b64decode
from time import sleep

from src.temp.temp_file_handler import TempFileHandler
from src.trial_network.trial_network_descriptor import get_component_public
from src.trial_network.trial_network_queries import get_descriptor_trial_network, update_status_trial_network
from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler

report_directory = os.path.join(os.getcwd(), "src", "callback", "reports")
decoded_component_information_file_path = os.path.join(report_directory, "decoded_component_information.json")
report_components_jenkins_file_path = os.path.join(report_directory, "report_components_jenkins.md")

class JenkinsHandler:

    def __init__(self):
        self.jenkins_server = os.getenv("JENKINS_SERVER")
        self.jenkins_user = os.getenv("JENKINS_USER")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD")
        self.jenkins_token = os.getenv("JENKINS_TOKEN")
        self.jenkins_job_name = os.getenv("JENKINS_JOB_NAME")
        self.jenkins_deployment_site = os.getenv("JENKINS_DEPLOYMENT_SITE")
        if self.jenkins_server and self.jenkins_user and self.jenkins_password:
            self.jenkins_client = Jenkins(self.jenkins_server, username=self.jenkins_user, password=self.jenkins_password)
        else:
            raise ValueError("Add the value of the variables JENKINS_SERVER, JENKINS_USER and JENKINS_PASSWORD in the .env file")
        if not self.jenkins_token or not self.jenkins_job_name or not self.jenkins_deployment_site:
            raise ValueError("Add the value of the variables JENKINS_TOKEN, JENKINS_JOB_NAME and JENKINS_DEPLOYMENT_SITE in the .env file")

    def jenkins_parameters(self, tn_id, component_name, branch=None, commit_id=None):
        return {
            "TN_ID": tn_id,
            "LIBRARY_COMPONENT_NAME": component_name,
            "LIBRARY_BRANCH": branch or commit_id,
            "DEPLOYMENT_SITE": self.jenkins_deployment_site,
        }
    
    def save_decoded_information(self, data):
        if os.path.isfile(decoded_component_information_file_path):
            os.remove(decoded_component_information_file_path)
        data["result_msg"] = b64decode(data["result_msg"]).decode("utf-8")
        with open(decoded_component_information_file_path, "w") as decoded_information_file:
            dump(data, decoded_information_file)
        result_msg = data["result_msg"]
        with open(report_components_jenkins_file_path, "a") as result_msg_file:
            result_msg_file.write(result_msg)

    def rename_decoded_information_file(self, name_file):
        new_name_path = os.path.join(report_directory, name_file)
        if os.path.isfile(decoded_component_information_file_path):
            os.rename(decoded_component_information_file_path, new_name_path)

    def extract_tn_vxlan_id(self, tn_id):
        component_report_file = os.path.join(report_directory, "tn_vxlan_" + tn_id + ".json")
        if os.path.isfile(component_report_file):
            with open(component_report_file, 'r') as file:
                json_data = load(file)
                tn_vxlan_id = json_data.get("tn_vxlan_id")
                return tn_vxlan_id

    def deploy_trial_network(self, tn_id, branch=None, commit_id=None):
        # TODO: raise JenkinsException in case something not working
        # check status trial network, if pending or failed start deploy
        sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
        sixglibrary_handler.git_clone_6glibrary()
        components_6glibrary = sixglibrary_handler.extract_components_6glibrary()
        if not os.path.exists(report_directory):
            os.makedirs(report_directory)
        if os.path.isfile(report_components_jenkins_file_path):
            os.remove(report_components_jenkins_file_path)
        temp_file_handler = TempFileHandler()
        descriptor_trial_network = get_descriptor_trial_network(tn_id)["trial_network"]
        update_status_trial_network(tn_id, "deploying")
        for component_name, component_data in descriptor_trial_network.items():
            if component_name in components_6glibrary:
                if component_name == "tn_vxlan":
                    component_path_temp_file = temp_file_handler.create_component_temp_file(component_name, get_component_public(component_data))
                else:
                    component_path_temp_file = temp_file_handler.create_component_temp_file(component_name, get_component_public(component_data), self.extract_tn_vxlan_id(tn_id))
                if os.path.isfile(component_path_temp_file):
                    with open(component_path_temp_file, 'rb') as component_temp_file:
                        file = {"FILE": (component_path_temp_file, component_temp_file)}
                        jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.jenkins_job_name, parameters=self.jenkins_parameters(tn_id, component_name, branch=branch, commit_id=commit_id))
                        response = post(jenkins_build_job_url, auth=(self.jenkins_user, self.jenkins_token), files=file)
                        if response.status_code == 201:
                            last_build_number = self.jenkins_client.get_job_info(name=self.jenkins_job_name)["nextBuildNumber"]
                            last_completed_builder = self.jenkins_client.get_job_info(name=self.jenkins_job_name)["lastCompletedBuild"]["number"]
                            while last_build_number != last_completed_builder:
                                sleep(15)
                            last_successful_build_number = self.jenkins_client.get_job_info(name=self.jenkins_job_name)["lastSuccessfulBuild"]["number"]
                            if last_successful_build_number == last_build_number:
                                sleep(5)
                                # TODO: Check if result is ok or not
                                self.rename_decoded_information_file(component_name + "_" + tn_id + ".json")
            else:
                # Raise and save status trial network
                print("Component not in 6G-Library")
        update_status_trial_network(tn_id, "finished")

    def jenkins_update_marketplace(self):
        # TODO: pipeline to update the TNLCM version in marketplace
        pass