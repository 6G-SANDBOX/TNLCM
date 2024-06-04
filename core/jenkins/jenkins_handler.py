import os

from jenkins import Jenkins
from requests import post
from time import sleep
from requests.exceptions import RequestException

from conf import JenkinsSettings, TnlcmSettings
from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import JenkinsConnectionError, JenkinsInvalidJobError, CustomFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError

class JenkinsHandler:

    def __init__(self, trial_network=None, temp_file_handler=None, callback_handler=None):
        """Constructor"""
        self.trial_network = trial_network
        self.temp_file_handler = temp_file_handler
        self.callback_handler = callback_handler
        self.jenkins_url = JenkinsSettings.JENKINS_URL
        self.jenkins_username = JenkinsSettings.JENKINS_USERNAME
        self.jenkins_password = JenkinsSettings.JENKINS_PASSWORD
        self.jenkins_token = JenkinsSettings.JENKINS_TOKEN
        self.tnlcm_callback = TnlcmSettings.TNLCM_CALLBACK
        self.deployment_job_name = JenkinsSettings.JENKINS_DEPLOYMENT_JOB_NAME
        self.destroy_job_name = JenkinsSettings.JENKINS_DESTROY_JOB_NAME
        try:
            self.jenkins_client = Jenkins(url=self.jenkins_url, username=self.jenkins_username, password=self.jenkins_password)
            self.jenkins_client.get_whoami()
        except RequestException:
            raise JenkinsConnectionError("Error establishing connection with Jenkins", 500)

    def set_deployment_job_name(self, deployment_job_name):
        """Set deployment job name in case of is correct job"""
        if deployment_job_name and deployment_job_name not in self.get_all_jobs():
            raise JenkinsInvalidJobError(f"The 'deployment_job_name' should be one: {', '.join(self.get_all_jobs())}", 404)
        if deployment_job_name:
            self.deployment_job_name = deployment_job_name
        log_handler.info(f"Pipeline use to deploy trial network: '{self.deployment_job_name}'")
    
    def _jenkins_deployment_parameters(self, component_type, custom_name, debug):
        """Return a dictionary with the parameters for each component to be passed to the deployment pipeline"""
        parameters = {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "COMPONENT_TYPE": component_type,
            "DEPLOYMENT_SITE": self.trial_network.deployment_site,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # OPTIONAL
            # "LIBRARY_URL": self.trial_network.github_6g_library_https_url,
            "LIBRARY_BRANCH": self.trial_network.github_6g_library_reference,
            # "SITES_URL": self.trial_network.github_6g_sandbox_sites_https_url,
            "SITES_BRANCH": self.trial_network.github_6g_sandbox_sites_reference,
            "DEBUG": debug
        }
        if custom_name:
            parameters["CUSTOM_NAME"] = custom_name
        return parameters

    def trial_network_deployment(self):
        """Trial network deployment starts"""
        tn_deployed_descriptor = self.trial_network.json_to_descriptor(self.trial_network.tn_deployed_descriptor)["trial_network"]
        tn_descriptor = tn_deployed_descriptor.copy()
        for entity_name, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            custom_name = None
            if "name" in entity_data:
                custom_name = entity_data["name"]
            debug = False
            if "debug" in entity_data:
                debug = entity_data["debug"]
            log_handler.info(f"Start the deployment of the '{entity_name}' entity")
            entity_path_temp_file = self.temp_file_handler.create_temp_file(entity_data["input"])
            if not os.path.exists(entity_path_temp_file):
                raise CustomFileNotFoundError(f"Temporary entity file '{entity_name}' not found", 404)
            with open(entity_path_temp_file, "rb") as component_temp_file:
                file = {"FILE": (entity_path_temp_file, component_temp_file)}
                log_handler.info(f"Add Jenkins parameters to the pipeline of the '{entity_name}' entity")
                jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.deployment_job_name, parameters=self._jenkins_deployment_parameters(component_type, custom_name, debug))
                response = post(jenkins_build_job_url, auth=(self.jenkins_username, self.jenkins_token), files=file)
                log_handler.info(f"Deployment request code of the '{entity_name}' entity '{response.status_code}'")
                if response.status_code != 201:
                    self.trial_network.set_tn_state("failed")
                    self.trial_network.save()
                    raise JenkinsResponseError(f"Error in the response received by Jenkins when trying to deploy the '{entity_name}' entity", response.status_code)
                last_build_number = self.jenkins_client.get_job_info(name=self.deployment_job_name)["nextBuildNumber"]
                while last_build_number != self.jenkins_client.get_job_info(name=self.deployment_job_name)["lastCompletedBuild"]["number"]:
                    sleep(15)
                if self.jenkins_client.get_job_info(name=self.deployment_job_name)["lastSuccessfulBuild"]["number"] != last_build_number:
                    self.trial_network.set_tn_state("failed")
                    self.trial_network.save()
                    raise JenkinsComponentPipelineError(f"Pipeline for the entity '{entity_name}' has failed", 500)
                log_handler.info(f"Entity '{entity_name}' successfully deployed")
                if not self.callback_handler.exists_path_entity_trial_network(entity_name):
                    self.trial_network.set_tn_state("failed")
                    self.trial_network.save()
                    raise CustomFileNotFoundError(f"File with the results of the entity '{entity_name}' not found", 404)
            del tn_deployed_descriptor[entity_name]
            self.trial_network.set_tn_deployed_descriptor(tn_deployed_descriptor)
            self.trial_network.save()
            log_handler.info(f"End of deployment of entity '{entity_name}'")
        log_handler.info("All entities of the trial network are deployed")

    def set_destroy_job_name(self, destroy_job_name):
        """Set destroy job name in case of is correct job"""
        if destroy_job_name and destroy_job_name not in self.get_all_jobs():
            raise JenkinsInvalidJobError(f"The 'destroy_job_name' should be one: {', '.join(self.get_all_jobs())}", 404)
        if destroy_job_name:
            self.destroy_job_name = destroy_job_name
        log_handler.info(f"Pipeline use to destroy trial network: '{self.destroy_job_name}'")
    
    def _jenkins_destroy_parameters(self):
        """Return a dictionary with the parameters for each component to be passed to the destroy pipeline"""
        parameters = {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "DEPLOYMENT_SITE": self.trial_network.deployment_site,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # OPTIONAL
            # "LIBRARY_URL": self.trial_network.github_6g_library_https_url,
            "LIBRARY_BRANCH": self.trial_network.github_6g_library_reference,
            # "SITES_URL": self.trial_network.github_6g_sandbox_sites_https_url,
            "SITES_BRANCH": self.trial_network.github_6g_sandbox_sites_reference,
            # "DEBUG": debug
        }
        return parameters
    
    def trial_network_destroy(self):
        """Trial network destroy starts"""
        jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.deployment_job_name, parameters=self._jenkins_destroy_parameters())
        response = post(jenkins_build_job_url, auth=(self.jenkins_username, self.jenkins_token))
        if response.status_code == 201:
            last_build_number = self.jenkins_client.get_job_info(name=self.deployment_job_name)["nextBuildNumber"]
            while last_build_number != self.jenkins_client.get_job_info(name=self.deployment_job_name)["lastCompletedBuild"]["number"]:
                sleep(15)
            if self.jenkins_client.get_job_info(name=self.deployment_job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                log_handler.info(f"Trial network '{self.trial_network.tn_id}' successfully destroyed")

    def get_all_jobs(self):
        """Return all the jobs/pipelines stored in Jenkins"""
        return [job["fullname"] for job in self.jenkins_client.get_all_jobs() if "fullname" in job and "jobs" not in job]