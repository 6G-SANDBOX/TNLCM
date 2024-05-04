import os

from jenkins import Jenkins
from requests import post
from requests.exceptions import RequestException

from time import sleep

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import JenkinsConnectionError, VariablesNotDefinedInEnvError, SixGLibraryComponentNotFound, JenkinsComponentFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError, JenkinsDeploymentReportNotFoundError

JENKINS_DEPLOYMENT_SITES = ["uma", "athens", "fokus"]

class JenkinsHandler:

    def __init__(self, trial_network_handler=None, sixglibrary_handler=None, temp_file_handler=None, callback_handler=None):
        """Constructor"""
        self.trial_network_handler = trial_network_handler
        self.sixglibrary_handler = sixglibrary_handler
        self.temp_file_handler = temp_file_handler
        self.callback_handler = callback_handler
        self.jenkins_server = os.getenv("JENKINS_SERVER")
        self.jenkins_user = os.getenv("JENKINS_USER")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD")
        self.jenkins_token = os.getenv("JENKINS_TOKEN")
        self.jenkins_pipeline_name = os.getenv("JENKINS_PIPELINE_NAME")
        self.jenkins_deployment_site = os.getenv("JENKINS_DEPLOYMENT_SITE")
        self.tnlcm_callback = os.getenv("TNLCM_CALLBACK")
        missing_variables = []
        if not self.jenkins_server:
            missing_variables.append("JENKINS_SERVER")
        if not self.jenkins_user:
            missing_variables.append("JENKINS_USER")
        if not self.jenkins_password:
            missing_variables.append("JENKINS_PASSWORD")
        if not self.jenkins_token:
            missing_variables.append("JENKINS_TOKEN")
        if not self.jenkins_pipeline_name:
            missing_variables.append("JENKINS_PIPELINE_NAME")
        if not self.jenkins_deployment_site:
            missing_variables.append("JENKINS_DEPLOYMENT_SITE")
        if not self.tnlcm_callback:
            missing_variables.append("TNLCM_CALLBACK")
        if missing_variables:
            raise VariablesNotDefinedInEnvError(f"Add the value of the variables {', '.join(missing_variables)} in the .env file", 500)
        self.jenkins_deployment_site = self.jenkins_deployment_site.lower()
        if self.jenkins_deployment_site not in JENKINS_DEPLOYMENT_SITES:
            raise VariablesNotDefinedInEnvError(f"The value of the variable 'JENKINS_DEPLOYMENT_SITE' should be {', '.join(JENKINS_DEPLOYMENT_SITES)} in the .env file", 500)
        try:
            self.jenkins_client = Jenkins(self.jenkins_server, username=self.jenkins_user, password=self.jenkins_password)
            self.jenkins_client.get_whoami()
        except RequestException:
            raise JenkinsConnectionError("Error establishing connection with Jenkins", 500)

    def _jenkins_parameters(self, library_component_name, entity_name):
        """Return a dictionary with the parameters for each component to be passed to the Jenkins pipeline"""
        log_handler.info(f"Add jenkins parameters to the pipeline of the '{entity_name}' entity which is '{library_component_name}' component")
        return {
            "TN_ID": self.trial_network_handler.tn_id,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # "LIBRARY_URL": self.sixglibrary_handler.git_6glibrary_https_url, # Optional
            "LIBRARY_COMPONENT_NAME": library_component_name,
            "ENTITY_NAME": entity_name,
            "LIBRARY_BRANCH": self.sixglibrary_handler.git_6glibrary_branch or self.sixglibrary_handler.git_6glibrary_commit_id, # Optional
            "DEPLOYMENT_SITE": self.jenkins_deployment_site,
        }

    def trial_network_deployment(self):
        """Trial network deployment starts"""
        self.sixglibrary_handler.git_clone_6glibrary()
        components_6glibrary = self.sixglibrary_handler.extract_components_6glibrary()
        self.trial_network_handler.update_trial_network_status("deploying")
        tn_descriptor = self.trial_network_handler.get_trial_network_descriptor()["trial_network"]
        for entity_name, entity_data in tn_descriptor.items():
            log_handler.info(f"Start the deployment of the '{entity_name}' entity")            
            library_component_name = entity_data["type"]
            if library_component_name in components_6glibrary:
                content = self.callback_handler.add_entity_input(entity_name, entity_data, self.jenkins_deployment_site)
                entity_path_temp_file = self.temp_file_handler.create_temp_file(content)
                if os.path.isfile(entity_path_temp_file):
                    with open(entity_path_temp_file, "rb") as component_temp_file:
                        file = {"FILE": (entity_path_temp_file, component_temp_file)}
                        jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.jenkins_pipeline_name, parameters=self._jenkins_parameters(self, library_component_name, entity_name))
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
                if self.sixglibrary_handler.git_6glibrary_branch is not None:
                    raise SixGLibraryComponentNotFound(f"Component '{library_component_name}' is not in '{self.sixglibrary_handler.git_6glibrary_branch}' branch of the 6G-Library", 404)
                else:
                    raise SixGLibraryComponentNotFound(f"Component '{library_component_name}' is not in commit_id '{self.sixglibrary_handler.git_6glibrary_commit_id}' of the 6G-Library", 404)
            log_handler.info(f"End of deployment of entity '{entity_name}'")
        self.trial_network_handler.update_trial_network_status("started")
        path_report_trial_network = self.callback_handler.get_path_report_trial_network()
        if os.path.exists(path_report_trial_network):
            self.trial_network_handler.add_report_trial_network(path_report_trial_network)
        else:
            raise JenkinsDeploymentReportNotFoundError("Trial network report file has not been found", 500)
        log_handler.info("All entities of the trial network are deployed")