import os

from yaml import dump
from jenkins import Jenkins
from requests import post
from time import sleep
from requests.exceptions import RequestException

from conf import JenkinsSettings, TnlcmSettings, SixGLibrarySettings, SixGSandboxSitesSettings
from core.logs.log_handler import log_handler
from core.models.trial_network import TrialNetworkModel
from core.callback.callback_handler import CallbackHandler
from core.sixg_library.sixg_library_handler import SixGLibraryHandler
from core.exceptions.exceptions_handler import JenkinsConnectionError, JenkinsInvalidPipelineError, CustomFileNotFoundError, JenkinsResponseError, JenkinsComponentPipelineError

class JenkinsHandler:

    def __init__(
        self, 
        trial_network: TrialNetworkModel = None, 
        callback_handler: CallbackHandler = None, 
        sixg_library_handler: SixGLibraryHandler = None, 
    ) -> None:
        """
        Constructor

        :param trial_network: model of the trial network to be deployed, ``TrialNetworkModel``
        :param callback_handler: handler to save results obtained by Jenkins, ``CallbackHandler``
        :param sixg_library_handler: handler to 6G-Library, ``SixGLibraryHandler``
        :raises JenkinsConnectionError: if the connection to Jenkins cannot be established (error code 500)
        """
        self.trial_network = trial_network
        self.callback_handler = callback_handler
        self.sixg_library_handler = sixg_library_handler
        self.jenkins_url = JenkinsSettings.JENKINS_URL
        self.jenkins_username = JenkinsSettings.JENKINS_USERNAME
        self.jenkins_password = JenkinsSettings.JENKINS_PASSWORD
        self.jenkins_token = JenkinsSettings.JENKINS_TOKEN
        self.tnlcm_callback = TnlcmSettings.TNLCM_CALLBACK
        try:
            self.jenkins_client = Jenkins(url=self.jenkins_url, username=self.jenkins_username, password=self.jenkins_password)
            self.jenkins_client.get_whoami()
        except RequestException:
            raise JenkinsConnectionError("Error establishing connection with Jenkins", 500)

    def generate_jenkins_deploy_pipeline(self) -> str:
        """
        Generate deployment pipeline per trial network

        :return: pipeline use for deploy trial network, ``str``
        :raises JenkinsInvalidPipelineError: if pipeline received by parameter is not defined in Jenkins (error code 404)
        """
        tn_deploy_pipeline = JenkinsSettings.JENKINS_DEPLOY_PIPELINE
        if tn_deploy_pipeline not in self.get_all_pipelines():
            raise JenkinsInvalidPipelineError(f"The 'jenkins_deploy_pipeline' should be one: {', '.join(self.get_all_pipelines())}", 404)
        tn_new_deploy_pipeline = f"{tn_deploy_pipeline}_{self.trial_network.tn_id}"
        config_tn_deploy_pipeline = self.jenkins_client.get_job_config(tn_deploy_pipeline)
        config_tn_new_deploy_pipeline = config_tn_deploy_pipeline.replace(tn_deploy_pipeline, tn_new_deploy_pipeline)
        self.jenkins_client.create_job(tn_new_deploy_pipeline, config_tn_new_deploy_pipeline)
        return tn_new_deploy_pipeline
    
    def _create_entity_name_input_file(self, entity_name: str, content: dict) -> str:
        """
        Return the path including the temporary file name
        
        :param entity_name: component type-name, ``str``
        :param content: content to be written into the temporary file, ``dict``
        :return: path to the file to be passed to Jenkins in which the component inputs are defined
        """
        log_handler.info(f"[{self.trial_network.tn_id}] - Create input file for entity '{entity_name}' to send to Jenkins pipeline")
        path_entity_name_input_file = os.path.join(self.trial_network.tn_folder, f"{self.trial_network.tn_id}-{entity_name}.yaml")
        with open(path_entity_name_input_file, 'w') as yaml_file:
            dump(content, yaml_file, default_flow_style=False)
        return path_entity_name_input_file

    def _jenkins_deployment_parameters(self, component_type: str, custom_name: str, debug: str) -> dict:
        """
        Function for create dictionary with the parameters for each component to be passed to the deployment pipeline

        :param component_type: type part of the descriptor file, ``str``
        :param custom_name: name part of the descriptor file, ``str``
        :param debug: debug part of the descriptor file (optional), ``str``
        :return: dictionary containing mandatory and optional parameters for the Jenkins deployment pipeline, ``dict``
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

    def trial_network_deployment(self) -> None:
        """
        Trial network deployment starts
        
        :raises CustomFileNotFoundError: if the temporary entity file or the results file of the entity is not found (error code 404)
        :raises JenkinsResponseError: if there is an error in the response from Jenkins during deployment (error code 401)
        :raises JenkinsComponentPipelineError: if the Jenkins pipeline for a specific entity fails (error code 500)
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
            log_handler.info(f"[{self.trial_network.tn_id}] - Start the deployment of the '{entity_name}' entity")
            path_entity_name_input_file = self._create_entity_name_input_file(entity_name, entity_data["input"])
            with open(path_entity_name_input_file, "rb") as entity_name_input_file:
                file = {"FILE": (path_entity_name_input_file, entity_name_input_file)}
                log_handler.info(f"[{self.trial_network.tn_id}] - Add Jenkins parameters to the pipeline of the '{entity_name}' entity")
                jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.trial_network.jenkins_deploy_pipeline, parameters=self._jenkins_deployment_parameters(component_type, custom_name, debug))
                response = post(jenkins_build_job_url, auth=(self.jenkins_username, self.jenkins_token), files=file)
                log_handler.info(f"[{self.trial_network.tn_id}] - Deployment request code of the '{entity_name}' entity '{response.status_code}'")
                if response.status_code != 201:
                    self.trial_network.set_tn_state("failed")
                    self.trial_network.save()
                    raise JenkinsResponseError(f"Error in the response received by Jenkins when trying to deploy the '{entity_name}' entity", response.status_code)
                last_build_number = self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["nextBuildNumber"]
                while not self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastCompletedBuild"]:
                    sleep(15)
                while last_build_number != self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastCompletedBuild"]["number"]:
                    sleep(15)
                if self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastSuccessfulBuild"]["number"] != last_build_number:
                    self.trial_network.set_tn_state("failed")
                    self.trial_network.save()
                    raise JenkinsComponentPipelineError(f"Pipeline for the entity '{entity_name}' has failed", 500)
                log_handler.info(f"[{self.trial_network.tn_id}] - Entity '{entity_name}' successfully deployed")
                if not self.callback_handler.exists_path_entity_name_json(entity_name):
                    self.trial_network.set_tn_state("failed")
                    self.trial_network.save()
                    raise CustomFileNotFoundError(f"File with the results of the entity '{entity_name}' not found", 404)
            del tn_deployed_descriptor[entity_name]
            self.trial_network.set_tn_deployed_descriptor(tn_deployed_descriptor)
            self.trial_network.save()
            log_handler.info(f"[{self.trial_network.tn_id}] - End of deployment of entity '{entity_name}'")

    def validate_jenkins_destroy_pipeline(self, jenkins_destroy_pipeline: str) -> str:
        """
        Set destroy pipeline name in case of is correct pipeline

        :param jenkins_destroy_pipeline: new name of the destroy pipeline, ``str``
        :return: pipeline use for destroy trial network, ``str``
        :raises JenkinsInvalidPipelineError: if pipeline received by parameter is not defined in Jenkins (error code 404)
        """
        if not jenkins_destroy_pipeline:
            return JenkinsSettings.JENKINS_DESTROY_PIPELINE
        if jenkins_destroy_pipeline and jenkins_destroy_pipeline not in self.get_all_pipelines():
            raise JenkinsInvalidPipelineError(f"The 'jenkins_destroy_pipeline' should be one: {', '.join(self.get_all_pipelines())}", 404)
        return jenkins_destroy_pipeline

    def _jenkins_destroy_parameters(self) -> dict:
        """
        Function for create dictionary with the parameters for each component to be passed to the destroy pipeline

        :return: dictionary containing mandatory and optional parameters for the Jenkins destroy pipeline, ``dict``
        """
        tn_components_types = self.trial_network.get_tn_components_types()
        metadata_part = self.sixg_library_handler.get_tn_components_parts(deployment_site=self.trial_network.deployment_site, parts=["metadata"], tn_components_types=tn_components_types)["metadata"]
        tn_sorted_descriptor = self.trial_network.json_to_descriptor(self.trial_network.tn_sorted_descriptor)["trial_network"]
        entities_with_destroy_script = []
        for entity_name, entity_data in tn_sorted_descriptor.items():
            component_type = entity_data["type"]
            if "destroy_script" in metadata_part[component_type] and metadata_part[component_type]["destroy_script"]:
                entities_with_destroy_script.append(entity_name)
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
            # "SCRIPTED_DESTROY_COMPONENTS": entities_with_destroy_script
            # "DEBUG": true
        }

    def trial_network_destroy(self, jenkins_destroy_pipeline: str) -> None:
        """
        Trial network destroy starts

        :param jenkins_destroy_pipeline: new name of the destroy pipeline, ``str``
        :raises JenkinsComponentPipelineError: if the Jenkins pipeline for a specific entity fails (error code 500)
        """
        self.jenkins_client.build_job(name=jenkins_destroy_pipeline, parameters=self._jenkins_destroy_parameters(), token=self.jenkins_token)
        last_build_number = self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["nextBuildNumber"]
        while not self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastCompletedBuild"]:
            sleep(15)
        while last_build_number != self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastCompletedBuild"]["number"]:
            sleep(15)
        if self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastSuccessfulBuild"]["number"] != last_build_number:
            raise JenkinsComponentPipelineError(f"Pipeline for destroy '{self.trial_network.tn_id}' trial network has failed", 500)

    def get_all_pipelines(self) -> list[str]:
        """
        Function to get all the pipelines stored in Jenkins

        :return: list with pipelines stored in Jenkins, ``list[str]``
        """
        return [job["fullname"] for job in self.jenkins_client.get_all_jobs() if "fullname" in job and "jobs" not in job]