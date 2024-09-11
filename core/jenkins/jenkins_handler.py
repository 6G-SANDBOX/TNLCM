import os

from jenkins import Jenkins
from requests import post
from time import sleep
from requests.exceptions import RequestException

from conf import JenkinsSettings, TnlcmSettings, SixGLibrarySettings, SixGSandboxSitesSettings
from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import JenkinsConnectionError, JenkinsInvalidJobError, CustomFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError

class JenkinsHandler:

    def __init__(self, trial_network=None, temp_file_handler=None, callback_handler=None, sixg_library_handler=None, sixg_sandbox_sites_handler=None):
        """
        Constructor

        :param trial_network: model of the trial network to be deployed, ``TrialNetworkModel``
        :param temp_file_handler: handler to create temporary files, ``TempFileHandler``
        :param callback_handler: handler to save results obtained by Jenkins, ``CallbackHandler``
        """
        self.trial_network = trial_network
        self.temp_file_handler = temp_file_handler
        self.callback_handler = callback_handler
        self.sixg_library_handler = sixg_library_handler
        self.sixg_sandbox_sites_handler = sixg_sandbox_sites_handler
        self.jenkins_url = JenkinsSettings.JENKINS_URL
        self.jenkins_username = JenkinsSettings.JENKINS_USERNAME
        self.jenkins_password = JenkinsSettings.JENKINS_PASSWORD
        self.jenkins_token = JenkinsSettings.JENKINS_TOKEN
        self.tnlcm_callback = TnlcmSettings.TNLCM_CALLBACK
        self.deployment_job_name = JenkinsSettings.JENKINS_JOB_DEPLOY
        self.destroy_job_name = JenkinsSettings.JENKINS_JOB_DESTROY
        try:
            self.jenkins_client = Jenkins(url=self.jenkins_url, username=self.jenkins_username, password=self.jenkins_password)
            self.jenkins_client.get_whoami()
        except RequestException:
            raise JenkinsConnectionError("Error establishing connection with Jenkins", 500)

    def set_deployment_job_name(self, deployment_job_name):
        """
        Set deployment job name in case of is correct job
        
        :param deployment_job_name: new name of the deployment job, ``str``
        """
        if deployment_job_name and deployment_job_name not in self.get_all_jobs():
            raise JenkinsInvalidJobError(f"The 'deployment_job_name' should be one: {', '.join(self.get_all_jobs())}", 404)
        if deployment_job_name:
            self.deployment_job_name = deployment_job_name
        log_handler.info(f"Pipeline use to deploy trial network: '{self.deployment_job_name}'")
    
    def _jenkins_deployment_parameters(self, component_type, custom_name, debug):
        """
        Return a dictionary with the parameters for each component to be passed to the deployment pipeline
        
        :param component_type: type part of the descriptor file, ``str``
        :param custom_name: name part of the descriptor file, ``str``
        :param debug: debug part of the descriptor file (optional), ``str``
        """
        parameters = {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "COMPONENT_TYPE": component_type,
            "DEPLOYMENT_SITE": self.trial_network.deployment_site,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # OPTIONAL
            "LIBRARY_URL": SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL,
            "LIBRARY_BRANCH": self.trial_network.github_6g_library_commit_id,
            "SITES_URL": SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL,
            "SITES_BRANCH": self.trial_network.github_6g_sandbox_sites_commit_id,
            "DEBUG": debug
        }
        if custom_name:
            parameters["CUSTOM_NAME"] = custom_name
        return parameters

    def trial_network_deployment(self):
        """
        Trial network deployment starts
        """
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
                while not self.jenkins_client.get_job_info(name=self.deployment_job_name)["lastCompletedBuild"]:
                    sleep(15)
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
        """
        Set destroy job name in case of is correct job
        
        :param destroy_job_name: new name of the destroy job, ``str``
        """
        if destroy_job_name and destroy_job_name not in self.get_all_jobs():
            raise JenkinsInvalidJobError(f"The 'destroy_job_name' should be one: {', '.join(self.get_all_jobs())}", 404)
        if destroy_job_name:
            self.destroy_job_name = destroy_job_name
        log_handler.info(f"Pipeline use to destroy trial network: '{self.destroy_job_name}'")
    
    def _jenkins_destroy_parameters(self):
        """
        Return a dictionary with the parameters for each component to be passed to the destroy pipeline
        """
        site_available_components = self.sixg_sandbox_sites_handler.get_site_available_components()
        list_site_available_components = list(site_available_components.keys())
        parts_components = self.sixg_library_handler.get_parts_components(site=self.trial_network.deployment_site, list_site_available_components=list_site_available_components)
        metadata = {component: data["metadata"] for component, data in parts_components.items()}
        tn_sorted_descriptor = self.trial_network.json_to_descriptor(self.trial_network.tn_sorted_descriptor)["trial_network"]
        entities_with_destroy_script = []
        for entity_name, entity_data in tn_sorted_descriptor.items():
            component_type = entity_data["type"]
            if "destroy_script" in metadata[component_type] and metadata[component_type]["destroy_script"]:
                entities_with_destroy_script.append(entity_name)
        print(entities_with_destroy_script)
        return {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "DEPLOYMENT_SITE": self.trial_network.deployment_site,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # OPTIONAL
            "LIBRARY_URL": SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL,
            "LIBRARY_BRANCH": self.trial_network.github_6g_library_commit_id,
            "SITES_URL": SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL,
            "SITES_BRANCH": self.trial_network.github_6g_sandbox_sites_commit_id,
            "SCRIPTED_DESTROY_COMPONENTS": entities_with_destroy_script
            # "DEBUG": true
        }
    
    def trial_network_destroy(self):
        """
        Trial network destroy starts
        """
        parameters=self._jenkins_destroy_parameters()
        # self.jenkins_client.build_job(name=self.destroy_job_name, parameters=self._jenkins_destroy_parameters(), token=self.jenkins_token)
        log_handler.info(f"Start the destroyed of the '{self.trial_network.tn_id}' trial network")
        last_build_number = self.jenkins_client.get_job_info(name=self.destroy_job_name)["nextBuildNumber"]
        while not self.jenkins_client.get_job_info(name=self.destroy_job_name)["lastCompletedBuild"]:
            sleep(15)
        while last_build_number != self.jenkins_client.get_job_info(name=self.destroy_job_name)["lastCompletedBuild"]["number"]:
            sleep(15)
        if self.jenkins_client.get_job_info(name=self.destroy_job_name)["lastSuccessfulBuild"]["number"] != last_build_number:
            raise JenkinsComponentPipelineError(f"Pipeline for destroy '{self.trial_network.tn_id}' trial network has failed", 500)
        log_handler.info(f"Trial network '{self.trial_network.tn_id}' successfully destroyed")

    def get_all_jobs(self):
        """
        Return all the jobs/pipelines stored in Jenkins
        """
        return [job["fullname"] for job in self.jenkins_client.get_all_jobs() if "fullname" in job and "jobs" not in job]