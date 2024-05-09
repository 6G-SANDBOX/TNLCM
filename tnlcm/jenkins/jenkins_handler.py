import os

from jenkins import Jenkins
from requests import post
from requests.exceptions import RequestException

from time import sleep

from tnlcm.logs.log_handler import log_handler
from tnlcm.exceptions.exceptions_handler import JenkinsConnectionError, VariablesNotDefinedInEnvError, SixGLibraryComponentNotFound, CustomFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError

JENKINS_DEPLOYMENT_SITES = ["uma", "athens", "fokus"]

class JenkinsHandler:

    def __init__(self, trial_network=None, sixglibrary_handler=None, sixgsandbox_sites_handler=None, temp_file_handler=None, callback_handler=None):
        """Constructor"""
        self.trial_network = trial_network
        self.sixglibrary_handler = sixglibrary_handler
        self.sixgsandbox_sites_handler = sixgsandbox_sites_handler
        self.temp_file_handler = temp_file_handler
        self.callback_handler = callback_handler
        self.jenkins_server = os.getenv("JENKINS_SERVER")
        self.jenkins_user = os.getenv("JENKINS_USER")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD")
        self.jenkins_token = os.getenv("JENKINS_TOKEN")
        self.jenkins_pipeline_folder = os.getenv("JENKINS_PIPELINE_FOLDER")
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
        self.jenkins_pipeline = None
        if not self.jenkins_pipeline_folder:
            self.jenkins_pipeline = self.jenkins_pipeline_name
        else:
            self.jenkins_pipeline = self.jenkins_pipeline_folder + "/" + self.jenkins_pipeline_name
        try:
            self.jenkins_client = Jenkins(self.jenkins_server, username=self.jenkins_user, password=self.jenkins_password)
            self.jenkins_client.get_whoami()
        except RequestException:
            raise JenkinsConnectionError("Error establishing connection with Jenkins", 500)

    def _jenkins_parameters(self, component_type, custom_name):
        """Return a dictionary with the parameters for each component to be passed to the Jenkins pipeline"""
        log_handler.info(f"Add jenkins parameters to the pipeline of the '{custom_name}' entity which is '{component_type}' component")
        return {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "COMPONENT_TYPE": component_type,
            "CUSTOM_NAME": custom_name,
            "DEPLOYMENT_SITE": self.jenkins_deployment_site,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # OPTIONAL
            "LIBRARY_URL": self.sixglibrary_handler.git_6glibrary_https_url,
            "LIBRARY_BRANCH": self.sixglibrary_handler.git_6glibrary_branch or self.sixglibrary_handler.git_6glibrary_commit_id,
            # "SITES_URL": self.sixgsandbox_sites_handler.git_6gsandbox_sites_https_url,
            "SITES_BRANCH": self.sixgsandbox_sites_handler.git_6gsandbox_sites_branch,
            # "DEBUG": False
        }

    def trial_network_deployment(self):
        """Trial network deployment starts"""
        self.sixglibrary_handler.git_clone_6glibrary()
        components_6glibrary = self.sixglibrary_handler.extract_components_6glibrary()
        tn_descriptor = self.trial_network.json_to_descriptor(self.trial_network.tn_sorted_descriptor)["trial_network"]
        for entity, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            custom_name = entity
            if "name" in entity_data:
                custom_name = entity_data["name"]
            log_handler.info(f"Start the deployment of the '{custom_name}' entity")
            if component_type in components_6glibrary:
                content = self.callback_handler.add_entity_input_parameters(custom_name, entity_data, self.jenkins_deployment_site)
                entity_path_temp_file = self.temp_file_handler.create_temp_file(content)
                if os.path.isfile(entity_path_temp_file):
                    with open(entity_path_temp_file, "rb") as component_temp_file:
                        file = {"FILE": (entity_path_temp_file, component_temp_file)}
                        jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.jenkins_pipeline, parameters=self._jenkins_parameters(component_type, custom_name))
                        response = post(jenkins_build_job_url, auth=(self.jenkins_user, self.jenkins_token), files=file)
                        log_handler.info(f"Deployment request code of the '{custom_name}' entity '{response.status_code}'")
                        if response.status_code == 201:
                            last_build_number = self.jenkins_client.get_job_info(name=self.jenkins_pipeline)["nextBuildNumber"]
                            while last_build_number != self.jenkins_client.get_job_info(name=self.jenkins_pipeline)["lastCompletedBuild"]["number"]:
                                sleep(15)
                            if self.jenkins_client.get_job_info(name=self.jenkins_pipeline)["lastSuccessfulBuild"]["number"] == last_build_number:
                                log_handler.info(f"Entity '{custom_name}' successfully deployed")
                                sleep(2)
                                if not self.callback_handler.exists_path_entity_trial_network(custom_name, component_type):
                                    raise CustomFileNotFoundError(f"File with the results of the entity '{custom_name}' not found", 404)
                            else:
                                raise JenkinsComponentPipelineError(f"Pipeline for the entity '{custom_name}' has failed", 500)
                        else:
                            raise JenkinsResponseError(f"Error in the response received by Jenkins when trying to deploy the '{custom_name}' entity", response.status_code)
                else:
                    raise CustomFileNotFoundError(f"Temporary entity file '{custom_name}' not found", 404)
            else:
                if self.sixglibrary_handler.git_6glibrary_branch:
                    raise SixGLibraryComponentNotFound(f"Component '{component_type}' is not in '{self.sixglibrary_handler.git_6glibrary_branch}' branch of the 6G-Library", 404)
                else:
                    raise SixGLibraryComponentNotFound(f"Component '{component_type}' is not in commit_id '{self.sixglibrary_handler.git_6glibrary_commit_id}' of the 6G-Library", 404)
            log_handler.info(f"End of deployment of entity '{custom_name}'")
        log_handler.info("All entities of the trial network are deployed")