import os

from jenkins import Jenkins
from requests import post
from requests.exceptions import RequestException

from time import sleep

from src.logs.log_handler import log_handler
from src.temp.temp_file_handler import TempFileHandler
from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler
from src.exceptions.exceptions_handler import JenkinsConnectionError, VariablesNotDefinedInEnvError, SixGLibraryComponentNotFound, JenkinsComponentFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError, JenkinsDeploymentReportNotFoundError

REPORT_DIRECTORY = os.path.join(os.getcwd(), "src", "callback", "reports")

class JenkinsHandler:

    def __init__(self, trial_network_handler=None):
        """Constructor"""
        self.jenkins_server = os.getenv("JENKINS_SERVER")
        self.jenkins_user = os.getenv("JENKINS_USER")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD")
        self.jenkins_token = os.getenv("JENKINS_TOKEN")
        self.jenkins_pipeline_name = os.getenv("JENKINS_PIPELINE_NAME")
        self.jenkins_deployment_site = os.getenv("JENKINS_DEPLOYMENT_SITE")
        if self.jenkins_server and self.jenkins_user and self.jenkins_password:
            try:
                self.jenkins_client = Jenkins(self.jenkins_server, username=self.jenkins_user, password=self.jenkins_password)
                self.jenkins_client.get_whoami()
            except RequestException:
                raise JenkinsConnectionError("Error establishing connection to Jenkins", 500)
        else:
            raise VariablesNotDefinedInEnvError("Add the value of the variables JENKINS_SERVER, JENKINS_USER and JENKINS_PASSWORD in the .env file", 500)
        if not self.jenkins_token or not self.jenkins_pipeline_name or not self.jenkins_deployment_site:
            raise VariablesNotDefinedInEnvError("Add the value of the variables JENKINS_TOKEN, JENKINS_PIPELINE_NAME and JENKINS_DEPLOYMENT_SITE in the .env file", 500)
        self.trial_network_handler = trial_network_handler
    
    def jenkins_parameters(self, tn_id, library_component_name, library_url, entity_name, branch=None, commit_id=None):
        """Return a dictionary with the parameters for each component to be passed to the jenkins pipeline"""
        return {
            "TN_ID": tn_id,
            "TNLCM_CALLBACK": os.getenv("TNLCM_CALLBACK"),
            # "LIBRARY_URL": library_url, # Optional
            "LIBRARY_COMPONENT_NAME": library_component_name,
            "ENTITY_NAME": entity_name,
            "LIBRARY_BRANCH": branch or commit_id, # Optional
            "DEPLOYMENT_SITE": self.jenkins_deployment_site,
        }

    def trial_network_deployment(self, branch=None, commit_id=None):
        """Trial network deployment starts"""
        sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
        sixglibrary_handler.git_clone_6glibrary()
        components_6glibrary = sixglibrary_handler.extract_components_6glibrary()
        self.trial_network_handler.update_trial_network_status("deploying")
        tn_descriptor = self.trial_network_handler.get_trial_network_descriptor()["trial_network"]
        tn_id = self.trial_network_handler.tn_id
        temp_file_handler = TempFileHandler()
        for entity_name, entity_data in tn_descriptor.items():
            log_handler.info(f"Starting the deployment of the '{entity_name}' entity")
            entity_name = entity_name + "_" + tn_id
            component_name = entity_data["type"]
            if component_name in components_6glibrary:
                entity_path_temp_file = temp_file_handler.create_entity_temp_file(entity_name, entity_data, tn_descriptor, REPORT_DIRECTORY, tn_id)
                if os.path.isfile(entity_path_temp_file):
                    with open(entity_path_temp_file, "rb") as component_temp_file:
                        file = {"FILE": (entity_path_temp_file, component_temp_file)}
                        jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.jenkins_pipeline_name, parameters=self.jenkins_parameters(tn_id, component_name, sixglibrary_handler.git_6glibrary_https_url, entity_name, branch=sixglibrary_handler.git_6glibrary_branch, commit_id=sixglibrary_handler.git_6glibrary_commit_id))
                        response = post(jenkins_build_job_url, auth=(self.jenkins_user, self.jenkins_token), files=file)
                        if response.status_code == 201:
                            last_build_number = self.jenkins_client.get_job_info(name=self.jenkins_pipeline_name)["nextBuildNumber"]
                            while last_build_number != self.jenkins_client.get_job_info(name=self.jenkins_pipeline_name)["lastCompletedBuild"]["number"]:
                                sleep(15)
                            if self.jenkins_client.get_job_info(name=self.jenkins_pipeline_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                                log_handler.info(f"Entity '{entity_name}' successfully deployed")
                            else:
                                raise JenkinsComponentPipelineError(f"Pipeline for the entity '{entity_name}' has failed", 500)
                        else:
                            raise JenkinsResponseError(f"Error in the response received by Jenkins when trying to deploy the '{entity_name}' entity", response.status_code)
                else:
                    raise JenkinsComponentFileNotFoundError(f"Entity file '{entity_name}' not found", 404)
            else:
                if branch is not None:
                    raise SixGLibraryComponentNotFound(f"Component '{component_name}' is not in '{branch}' branch of the 6G-Library", 404)
                else:
                    raise SixGLibraryComponentNotFound(f"Component '{component_name}' is not in commit_id '{commit_id}' of the 6G-Library", 404)
            log_handler.info(f"End of deployment of entity '{entity_name}'")
        self.trial_network_handler.update_trial_network_status("started")
        report_trial_network_name = tn_id + ".json"
        path_report_trial_network = os.path.join(REPORT_DIRECTORY, report_trial_network_name)
        if os.path.exists(path_report_trial_network):
            self.trial_network_handler.add_report_trial_network(path_report_trial_network)
        else:
            raise JenkinsDeploymentReportNotFoundError("Trial network report file has not been found", 500)
        log_handler.info("All entities of the trial network are deployed")