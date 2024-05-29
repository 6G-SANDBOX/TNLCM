import os

from jenkins import Jenkins
from requests import post
from time import sleep
from requests.exceptions import RequestException

from conf import JenkinsSettings
from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import JenkinsConnectionError, JenkinsInvalidJobError, CustomFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError

class JenkinsHandler:

    def __init__(self, trial_network=None, sixg_library_handler=None, sixg_sandbox_sites_handler=None, temp_file_handler=None, callback_handler=None, job_name=None):
        """Constructor"""
        self.trial_network = trial_network
        self.sixg_library_handler = sixg_library_handler
        self.sixg_sandbox_sites_handler = sixg_sandbox_sites_handler
        self.temp_file_handler = temp_file_handler
        self.callback_handler = callback_handler
        self.jenkins_url = JenkinsSettings.JENKINS_URL
        self.jenkins_username = JenkinsSettings.JENKINS_USERNAME
        self.jenkins_password = JenkinsSettings.JENKINS_PASSWORD
        self.jenkins_token = JenkinsSettings.JENKINS_TOKEN
        self.tnlcm_callback = JenkinsSettings.TNLCM_CALLBACK
        try:
            self.jenkins_client = Jenkins(url=self.jenkins_url, username=self.jenkins_username, password=self.jenkins_password)
            self.jenkins_client.get_whoami()
        except RequestException:
            raise JenkinsConnectionError("Error establishing connection with Jenkins", 500)
        self.job_name = job_name
        if not self.job_name:
            self.job_name = JenkinsSettings.JENKINS_JOB_NAME
        if self.job_name not in self.get_all_jobs():
            raise JenkinsInvalidJobError(f"The 'job_name' should be one: {', '.join(self.get_all_jobs())}", 400)

    def _jenkins_parameters(self, component_type, custom_name):
        """Return a dictionary with the parameters for each component to be passed to the Jenkins pipeline"""
        parameters = {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "COMPONENT_TYPE": component_type,
            "DEPLOYMENT_SITE": self.sixg_sandbox_sites_handler.deployment_site,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # OPTIONAL
            "LIBRARY_URL": self.sixg_library_handler.github_6g_library_https_url,
            "LIBRARY_BRANCH": self.sixg_library_handler.github_6g_library_branch,
            # "SITES_URL": self.sixg_sandbox_sites_handler.github_6g_sandbox_sites_https_url,
            "SITES_BRANCH": self.sixg_sandbox_sites_handler.github_6g_sandbox_sites_branch,
            # "DEBUG": False
        }
        if custom_name:
            parameters["CUSTOM_NAME"] = custom_name
        return parameters

    def trial_network_deployment(self):
        """Trial network deployment starts"""
        tn_descriptor = self.trial_network.json_to_descriptor(self.trial_network.tn_sorted_descriptor)["trial_network"]
        for entity_name, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            custom_name = None
            if "name" in entity_data:
                custom_name = entity_data["name"]
            log_handler.info(f"Start the deployment of the '{entity_name}' entity")
            entity_path_temp_file = self.temp_file_handler.create_temp_file(entity_data["input"])
            if not os.path.exists(entity_path_temp_file):
                raise CustomFileNotFoundError(f"Temporary entity file '{entity_name}' not found", 404)
            with open(entity_path_temp_file, "rb") as component_temp_file:
                file = {"FILE": (entity_path_temp_file, component_temp_file)}
                log_handler.info(f"Add jenkins parameters to the pipeline of the '{entity_name}' entity")
                jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.job_name, parameters=self._jenkins_parameters(component_type, custom_name))
                response = post(jenkins_build_job_url, auth=(self.jenkins_username, self.jenkins_token), files=file)
                log_handler.info(f"Deployment request code of the '{entity_name}' entity '{response.status_code}'")
                if response.status_code != 201:
                    raise JenkinsResponseError(f"Error in the response received by Jenkins when trying to deploy the '{entity_name}' entity", response.status_code)
                last_build_number = self.jenkins_client.get_job_info(name=self.job_name)["nextBuildNumber"]
                while last_build_number != self.jenkins_client.get_job_info(name=self.job_name)["lastCompletedBuild"]["number"]:
                    sleep(15)
                if self.jenkins_client.get_job_info(name=self.job_name)["lastSuccessfulBuild"]["number"] != last_build_number:
                    raise JenkinsComponentPipelineError(f"Pipeline for the entity '{entity_name}' has failed", 500)
                log_handler.info(f"Entity '{entity_name}' successfully deployed")
                sleep(2)
                if not self.callback_handler.exists_path_entity_trial_network(entity_name):
                    raise CustomFileNotFoundError(f"File with the results of the entity '{entity_name}' not found", 404)
            log_handler.info(f"End of deployment of entity '{entity_name}'")
        log_handler.info("All entities of the trial network are deployed")

    def get_all_jobs(self):
        """Return all the jobs/pipelines stored in Jenkins"""
        return [job["fullname"] for job in self.jenkins_client.get_all_jobs() if "fullname" in job and "jobs" not in job]