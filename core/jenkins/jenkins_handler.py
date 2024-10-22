import os

from requests import post
from time import sleep
from jenkins import Jenkins, JenkinsException
from requests.exceptions import RequestException

from conf import JenkinsSettings, TnlcmSettings, SixGLibrarySettings, SixGSandboxSitesSettings
from core.logs.log_handler import log_handler
from core.models import CallbackModel, TrialNetworkModel
from core.sixg_library.sixg_library_handler import SixGLibraryHandler
from core.utils.file_handler import save_yaml
from core.exceptions.exceptions_handler import CustomJenkinsException

class JenkinsHandler:

    def __init__(
        self, 
        trial_network: TrialNetworkModel = None, 
        sixg_library_handler: SixGLibraryHandler = None, 
    ) -> None:
        """
        Constructor

        :param trial_network: model of the trial network to be deployed, ``TrialNetworkModel``
        :param sixg_library_handler: handler to 6G-Library, ``SixGLibraryHandler``
        :raises JenkinsConnectionError:
        """
        self.trial_network = trial_network
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
            raise CustomJenkinsException("Error establishing connection with Jenkins", 500)

    def _is_folder_jenkins(self, folder_name: str) -> bool:
        """
        Check if a Jenkins folder exists

        :param folder_name: name of the folder to check, ``str``
        :return: True if the folder exists, False otherwise, ``bool``
        """
        try:
            self.jenkins_client.get_job_info(folder_name)
            return True
        except JenkinsException:
            return False

    def generate_jenkins_deploy_pipeline(self, jenkins_deploy_pipeline: str) -> str:
        """
        Generate deployment pipeline per trial network

        :param jenkins_deploy_pipeline: new name of the deployment pipeline, ``str``
        :return: pipeline use for deploy trial network, ``str``
        :raises CustomJenkinsException:
        """
        if not jenkins_deploy_pipeline:
            tn_deploy_pipeline = JenkinsSettings.JENKINS_DEPLOY_PIPELINE
            if tn_deploy_pipeline not in self.get_all_pipelines():
                raise CustomJenkinsException(f"The 'jenkins_deploy_pipeline' should be one: {', '.join(self.get_all_pipelines())}", 404)
            tn_jenkins = "TNLCM"
            if not self._is_folder_jenkins(tn_jenkins):
                self.jenkins_client.create_folder(tn_jenkins)
            tn_new_deploy_pipeline = f"{tn_deploy_pipeline}_{self.trial_network.tn_id}"
            config_tn_deploy_pipeline = self.jenkins_client.get_job_config(tn_deploy_pipeline)
            config_tn_new_deploy_pipeline = config_tn_deploy_pipeline.replace(tn_deploy_pipeline, tn_new_deploy_pipeline)
            config_tn_new_deploy_pipeline = config_tn_new_deploy_pipeline.replace(f"{tn_new_deploy_pipeline}.groovy", f"{tn_deploy_pipeline}.groovy")
            tn_jenkins_deploy_path = f"{tn_jenkins}/{tn_new_deploy_pipeline}"
            self.jenkins_client.create_job(tn_jenkins_deploy_path, config_tn_new_deploy_pipeline)
            log_handler.info(f"[{self.trial_network.tn_id}] - Created '{tn_jenkins_deploy_path}' pipeline in Jenkins to deploy the trial network")
            return tn_jenkins_deploy_path
        else:
            if jenkins_deploy_pipeline not in self.get_all_pipelines():
                raise CustomJenkinsException(f"The 'jenkins_deploy_pipeline' should be one: {', '.join(self.get_all_pipelines())}", 404)
            if self.jenkins_client.get_job_info(jenkins_deploy_pipeline)["inQueue"]:
                raise CustomJenkinsException(f"The pipeline '{jenkins_deploy_pipeline}' is currently in use. Try again later", 500)
            log_handler.info(f"[{self.trial_network.tn_id}] - Use the pipeline '{jenkins_deploy_pipeline}' defined in Jenkins to deploy the trial network")
            return jenkins_deploy_pipeline

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
        
        :raises CustomJenkinsException:
        """
        deployed_descriptor = self.trial_network.deployed_descriptor["trial_network"]
        tn_descriptor = deployed_descriptor.copy()
        for entity_name, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            custom_name = None
            if "name" in entity_data:
                custom_name = entity_data["name"]
            debug = False
            if "debug" in entity_data:
                debug = entity_data["debug"]
            log_handler.info(f"[{self.trial_network.tn_id}] - Start deployment of the '{entity_name}' entity")
            entity_name_input_file_path = os.path.join(self.trial_network.directory_path, f"{self.trial_network.tn_id}-{entity_name}.yaml")
            save_yaml(data=dict(entity_data["input"]), file_path=entity_name_input_file_path)
            log_handler.info(f"[{self.trial_network.tn_id}] - Created input file for entity '{entity_name}' to send to Jenkins pipeline")
            with open(entity_name_input_file_path, "rb") as entity_name_input_file:
                file = {"FILE": (entity_name_input_file_path, entity_name_input_file)}
                log_handler.info(f"[{self.trial_network.tn_id}] - Add Jenkins parameters to the pipeline of the '{entity_name}' entity")
                jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.trial_network.jenkins_deploy_pipeline, parameters=self._jenkins_deployment_parameters(component_type, custom_name, debug))
                response = post(jenkins_build_job_url, auth=(self.jenkins_username, self.jenkins_token), files=file)
                log_handler.info(f"[{self.trial_network.tn_id}] - Deployment request code of the '{entity_name}' entity '{response.status_code}'")
                if response.status_code != 201:
                    raise CustomJenkinsException(f"Error in the response received by Jenkins when trying to deploy the '{entity_name}' entity", response.status_code)
                next_build_number = self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["nextBuildNumber"]
                while not self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastCompletedBuild"]:
                    log_handler.info(f"[{self.trial_network.tn_id}] - Deploying '{entity_name}'")
                    sleep(10)
                while next_build_number != self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastCompletedBuild"]["number"]:
                    log_handler.info(f"[{self.trial_network.tn_id}] - Deploying '{entity_name}'")
                    sleep(10)
                if self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastSuccessfulBuild"]["number"] != next_build_number:
                    raise CustomJenkinsException(f"Pipeline for the entity '{entity_name}' has failed", 500)
                log_handler.info(f"[{self.trial_network.tn_id}] - Entity '{entity_name}' successfully deployed")
                sleep(3)
                callback = CallbackModel.objects(tn_id=self.trial_network.tn_id, entity_name=entity_name).first()
                if not callback:
                    raise CustomJenkinsException(f"Callback with the results of the entity '{entity_name}' not found", 404)
                del deployed_descriptor[entity_name]
                self.trial_network.set_deployed_descriptor(deployed_descriptor)
                self.trial_network.save()
                log_handler.info(f"[{self.trial_network.tn_id}] - End of deployment of entity '{entity_name}'")
            if not os.path.join(f"{self.trial_network.directory_path}", f"{self.trial_network.tn_id}.md"):
                raise CustomJenkinsException(f"File with the report of the trial network '{self.trial_network.tn_id}' not found", 404)

    def generate_jenkins_destroy_pipeline(self, jenkins_destroy_pipeline: str) -> str:
        """
        Generate destroy pipeline per trial network

        :param jenkins_destroy_pipeline: new name of the destroy pipeline, ``str``
        :return: pipeline use for destroy trial network, ``str``
        :raises CustomJenkinsException:
        """
        if not jenkins_destroy_pipeline:
            tn_destroy_pipeline = JenkinsSettings.JENKINS_DESTROY_PIPELINE
            if tn_destroy_pipeline not in self.get_all_pipelines():
                raise CustomJenkinsException(f"The 'jenkins_destroy_pipeline' should be one: {', '.join(self.get_all_pipelines())}", 404)
            tn_jenkins = "TNLCM"
            tn_new_destroy_pipeline = f"{tn_destroy_pipeline}_{self.trial_network.tn_id}"
            config_tn_destroy_pipeline = self.jenkins_client.get_job_config(tn_destroy_pipeline)
            config_tn_new_destroy_pipeline = config_tn_destroy_pipeline.replace(tn_destroy_pipeline, tn_new_destroy_pipeline)
            config_tn_new_destroy_pipeline = config_tn_new_destroy_pipeline.replace(f"{tn_new_destroy_pipeline}.groovy", f"{tn_destroy_pipeline}.groovy")
            tn_jenkins_destroy_path = f"{tn_jenkins}/{tn_new_destroy_pipeline}"
            self.jenkins_client.create_job(tn_jenkins_destroy_path, config_tn_new_destroy_pipeline)
            log_handler.info(f"[{self.trial_network.tn_id}] - Created '{tn_jenkins_destroy_path}' pipeline in Jenkins to destroy the trial network")
            return tn_jenkins_destroy_path
        else:
            if jenkins_destroy_pipeline not in self.get_all_pipelines():
                raise CustomJenkinsException(f"The 'jenkins_destroy_pipeline' should be one: {', '.join(self.get_all_pipelines())}", 404)
            if self.jenkins_client.get_job_info(jenkins_destroy_pipeline)["inQueue"]:
                raise CustomJenkinsException(f"The pipeline '{jenkins_destroy_pipeline}' is currently in use. Try again later", 500)
            log_handler.info(f"[{self.trial_network.tn_id}] - Use the pipeline '{jenkins_destroy_pipeline}' defined in Jenkins to destroy the trial network")
            return jenkins_destroy_pipeline

    def _jenkins_destroy_parameters(self) -> dict:
        """
        Function for create dictionary with the parameters for each component to be passed to the destroy pipeline

        :return: dictionary containing mandatory and optional parameters for the Jenkins destroy pipeline, ``dict``
        """
        tn_components_types = self.trial_network.get_tn_components_types()
        metadata_part = self.sixg_library_handler.get_tn_components_parts(parts=["metadata"], tn_components_types=tn_components_types)["metadata"]
        sorted_descriptor = self.trial_network.sorted_descriptor["trial_network"]
        entities_with_destroy_script = []
        for entity_name, entity_data in sorted_descriptor.items():
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
        :raises CustomJenkinsException:
        """
        self.jenkins_client.build_job(name=jenkins_destroy_pipeline, parameters=self._jenkins_destroy_parameters(), token=self.jenkins_token)
        last_build_number = self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["nextBuildNumber"]
        while not self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastCompletedBuild"]:
            log_handler.info(f"[{self.trial_network.tn_id}] - Destroying trial network")
            sleep(15)
        while last_build_number != self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastCompletedBuild"]["number"]:
            log_handler.info(f"[{self.trial_network.tn_id}] - Destroying trial network")
            sleep(15)
        if self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastSuccessfulBuild"]["number"] != last_build_number:
            raise CustomJenkinsException(f"Pipeline for destroy '{self.trial_network.tn_id}' trial network has failed", 500)

    def get_all_pipelines(self) -> list[str]:
        """
        Function to get all the pipelines stored in Jenkins

        :return: list with pipelines stored in Jenkins, ``list[str]``
        """
        return [job["fullname"] for job in self.jenkins_client.get_all_jobs() if "fullname" in job and "jobs" not in job]