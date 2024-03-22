import os

from jenkins import Jenkins
from requests import post
from requests.exceptions import RequestException
from json import load, dump
from base64 import b64decode
from time import sleep
from string import ascii_lowercase, digits
from random import choice

from src.temp.temp_file_handler import TempFileHandler
from src.trial_network.trial_network_descriptor import get_component_public
from src.trial_network.trial_network_queries import get_descriptor_trial_network, update_status_trial_network, save_report_trial_network, check_component_id, update_component_id_trial_network
from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler
from src.exceptions.exceptions_handler import JenkinsConnectionError, VariablesNotDefinedInEnvError, KeyNotFoundError, CustomUnicodeDecodeError, SixGLibraryComponentNotFound, JenkinsComponentFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError, JenkinsComponentReportNotFoundError, JenkinsDeploymentReportNotFoundError

REPORT_DIRECTORY = os.path.join(os.getcwd(), "src", "callback", "reports")
DECODED_COMPONENT_INFORMATION_FILE_PATH = os.path.join(REPORT_DIRECTORY, "decoded_component_information.json")
REPORT_COMPONENTS_JENKINS_FILE_PATH = os.path.join(REPORT_DIRECTORY, "report_components_jenkins.md")

class JenkinsHandler:

    def __init__(self):
        self.jenkins_server = os.getenv("JENKINS_SERVER")
        self.jenkins_user = os.getenv("JENKINS_USER")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD")
        self.jenkins_token = os.getenv("JENKINS_TOKEN")
        self.jenkins_job_name = os.getenv("JENKINS_JOB_NAME")
        self.jenkins_deployment_site = os.getenv("JENKINS_DEPLOYMENT_SITE")
        if self.jenkins_server and self.jenkins_user and self.jenkins_password:
            try:
                self.jenkins_client = Jenkins(self.jenkins_server, username=self.jenkins_user, password=self.jenkins_password)
                self.jenkins_client.get_whoami()
            except RequestException:
                raise JenkinsConnectionError("Error establishing connection to Jenkins", 500)
        else:
            raise VariablesNotDefinedInEnvError("Add the value of the variables JENKINS_SERVER, JENKINS_USER and JENKINS_PASSWORD in the .env file", 500)
        if not self.jenkins_token or not self.jenkins_job_name or not self.jenkins_deployment_site:
            raise VariablesNotDefinedInEnvError("Add the value of the variables JENKINS_TOKEN, JENKINS_JOB_NAME and JENKINS_DEPLOYMENT_SITE in the .env file", 500)

    def jenkins_parameters(self, tn_id, component_name, branch=None, commit_id=None):
        return {
            "TN_ID": tn_id,
            "LIBRARY_COMPONENT_NAME": component_name,
            "LIBRARY_BRANCH": branch or commit_id,
            "DEPLOYMENT_SITE": self.jenkins_deployment_site,
        }
    
    def save_decoded_information(self, data):
        try:
            if os.path.isfile(DECODED_COMPONENT_INFORMATION_FILE_PATH):
                os.remove(DECODED_COMPONENT_INFORMATION_FILE_PATH)
            if "result_msg" not in data:
                raise KeyNotFoundError(f"The result_msg key has not been received by Jenkins", 400)
            data["result_msg"] = b64decode(data["result_msg"]).decode("utf-8")
            with open(DECODED_COMPONENT_INFORMATION_FILE_PATH, "w") as decoded_information_file:
                dump(data, decoded_information_file)
            result_msg = data["result_msg"]
            with open(REPORT_COMPONENTS_JENKINS_FILE_PATH, "a") as result_msg_file:
                result_msg_file.write(result_msg)
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 500)

    def extract_tn_vxlan_id(self, component_id):
        component_report_file = os.path.join(REPORT_DIRECTORY, "tn_vxlan_" + component_id + ".json")
        if os.path.isfile(component_report_file):
            with open(component_report_file, "r") as file:
                json_data = load(file)
                tn_vxlan_id = json_data["tn_vxlan_id"]
                return tn_vxlan_id
    
    def generate_random_string(self, size=6, chars=ascii_lowercase + digits):
        return ''.join(choice(chars) for _ in range(size))

    def deploy_trial_network(self, user_created, tn_id, branch=None, commit_id=None):
        # Check status trial network, if pending or failed start deploy
        sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
        sixglibrary_handler.git_clone_6glibrary()
        components_6glibrary = sixglibrary_handler.extract_components_6glibrary()
        if not os.path.exists(REPORT_DIRECTORY):
            os.makedirs(REPORT_DIRECTORY)
        if os.path.isfile(REPORT_COMPONENTS_JENKINS_FILE_PATH):
            os.remove(REPORT_COMPONENTS_JENKINS_FILE_PATH)
        temp_file_handler = TempFileHandler()
        descriptor_trial_network = get_descriptor_trial_network(user_created, tn_id)["trial_network"]
        update_status_trial_network(user_created, tn_id, "deploying")
        component_id = user_created + "_" + tn_id + "_" + self.generate_random_string(size=3)
        while check_component_id(user_created, component_id):
            component_id = user_created + "_" + tn_id + "_" + self.generate_random_string(size=3)
        for component_name, component_data in descriptor_trial_network.items():
            if component_name in components_6glibrary:
                if component_name == "tn_vxlan":
                    component_path_temp_file = temp_file_handler.create_component_temp_file(component_name, get_component_public(component_data))
                else:
                    component_path_temp_file = temp_file_handler.create_component_temp_file(component_name, get_component_public(component_data), self.extract_tn_vxlan_id(component_id))
                if os.path.isfile(component_path_temp_file):
                    with open(component_path_temp_file, 'rb') as component_temp_file:
                        file = {"FILE": (component_path_temp_file, component_temp_file)}
                        jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.jenkins_job_name, parameters=self.jenkins_parameters(component_id, component_name, branch=branch, commit_id=commit_id))
                        response = post(jenkins_build_job_url, auth=(self.jenkins_user, self.jenkins_token), files=file)
                        if response.status_code == 201:
                            last_build_number = self.jenkins_client.get_job_info(name=self.jenkins_job_name)["nextBuildNumber"]
                            while last_build_number != self.jenkins_client.get_job_info(name=self.jenkins_job_name)["lastCompletedBuild"]["number"]:
                                sleep(15)
                            if self.jenkins_client.get_job_info(name=self.jenkins_job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                                sleep(2)
                                if os.path.isfile(DECODED_COMPONENT_INFORMATION_FILE_PATH):
                                    os.rename(DECODED_COMPONENT_INFORMATION_FILE_PATH, os.path.join(REPORT_DIRECTORY, component_name + "_" + component_id + ".json"))
                                else:
                                    raise JenkinsComponentReportNotFoundError(f"The '{component_name}' component deployment report file is not found", 500)
                            else:
                                raise JenkinsComponentPipelineError(f"The pipeline for the component '{component_name}' has failed", 500)
                        else:
                            raise JenkinsResponseError(f"Error in the response received by Jenkins when trying to deploy the '{component_name}' component", response.status_code)
                else:
                    raise JenkinsComponentFileNotFoundError("Component file not found", 404)
            else:
                if branch is not None:
                    raise SixGLibraryComponentNotFound(f"The '{component_name}' component is not in '{branch}' branch of the 6G-Library", 404)
                else:
                    raise SixGLibraryComponentNotFound(f"The '{component_name}' component is not in commit_id '{commit_id}' of the 6G-Library", 404)
        update_status_trial_network(user_created, tn_id, "finished")
        update_component_id_trial_network(user_created, tn_id, component_id)
        if os.path.exists(REPORT_COMPONENTS_JENKINS_FILE_PATH):
            save_report_trial_network(user_created, tn_id, REPORT_COMPONENTS_JENKINS_FILE_PATH)
        else:
            raise JenkinsDeploymentReportNotFoundError("The trial network report file has not been found", 500)

    def jenkins_update_marketplace(self):
        # TODO: pipeline to update the TNLCM version in marketplace
        pass