from jenkins import Jenkins
from requests import post
from requests.exceptions import RequestException
from time import sleep

from conf.jenkins import JenkinsSettings
from conf.tnlcm import TnlcmSettings
from core.logs.log_handler import TnLogHandler
from core.models.trial_network import TrialNetworkModel
from core.library.library_handler import LibraryHandler
from core.utils.file_handler import load_file, save_yaml
from core.utils.os_handler import exists_path, join_path
from core.exceptions.exceptions_handler import CustomJenkinsException

class JenkinsHandler:

    def __init__(
        self, 
        trial_network: TrialNetworkModel = None, 
        library_handler: LibraryHandler = None, 
    ) -> None:
        """
        Constructor

        :param trial_network: model of the trial network to be deployed, ``TrialNetworkModel``
        :param library_handler: Library handler, ``LibraryHandler``
        :raises JenkinsConnectionError:
        """
        self.trial_network = trial_network
        self.library_handler = library_handler
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
    
    def _is_folder_created(self, folder_name: str) -> bool:
        """
        Check if a Jenkins folder exists

        :param folder_name: name of the folder to check, ``str``
        :return: True if the folder exists, False otherwise, ``bool``
        """
        return any(job["name"] == folder_name for job in self.jenkins_client.get_jobs(folder_depth=0))

    def generate_jenkins_deploy_pipeline(self, jenkins_deploy_pipeline: str) -> str:
        """
        Generate deployment pipeline per trial network

        :param jenkins_deploy_pipeline: new name of the deployment pipeline, ``str``
        :return: pipeline use for deploy trial network, ``str``
        :raises CustomJenkinsException:
        """
        if jenkins_deploy_pipeline:
            pipelines = self.get_all_pipelines()
            if jenkins_deploy_pipeline not in pipelines:
                raise CustomJenkinsException(f"The jenkins_deploy_pipeline should be one: {pipelines}", 404)
            if self.jenkins_client.get_job_info(jenkins_deploy_pipeline)["inQueue"]:
                raise CustomJenkinsException(f"The pipeline {jenkins_deploy_pipeline} is currently in use. Try again later", 500)
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Using existing pipeline {jenkins_deploy_pipeline} to deploy the trial network")
            return jenkins_deploy_pipeline

        tn_deploy_pipeline = JenkinsSettings.JENKINS_DEPLOY_PIPELINE
        tn_new_deploy_pipeline = f"{tn_deploy_pipeline}_{self.trial_network.tn_id}"
        if not self._is_folder_created("TNLCM"):
            self.jenkins_client.create_folder("TNLCM")

        config = self.jenkins_client.get_job_config(tn_deploy_pipeline)
        config = config.replace(tn_deploy_pipeline, tn_new_deploy_pipeline)
        config = config.replace(f"{tn_new_deploy_pipeline}.groovy", f"{tn_deploy_pipeline}.groovy")
        
        tn_jenkins_deploy_path = f"TNLCM/{tn_new_deploy_pipeline}"
        self.jenkins_client.create_job(tn_jenkins_deploy_path, config)
        TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Created {tn_jenkins_deploy_path} pipeline in Jenkins to deploy the trial network")
        
        return tn_jenkins_deploy_path

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
            "LIBRARY_URL": self.trial_network.library_https_url,
            "LIBRARY_BRANCH": self.trial_network.library_commit_id,
            "SITES_URL": self.trial_network.sites_https_url,
            "SITES_BRANCH": self.trial_network.sites_commit_id,
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
        deployed_descriptor = self.trial_network.to_mongo()["deployed_descriptor"]["trial_network"]
        deployed_descriptor_copy = deployed_descriptor.copy()
        for entity_name, entity_data in deployed_descriptor_copy.items():
            component_type = entity_data["type"]
            custom_name = None
            if "name" in entity_data:
                custom_name = entity_data["name"]
            debug = False
            if "debug" in entity_data:
                debug = entity_data["debug"]
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Start deployment of the {entity_name} entity")
            entity_name_input_file_path = join_path(self.trial_network.directory_path, "input", f"{self.trial_network.tn_id}-{entity_name}.yaml")
            entity_name_input = entity_data["input"]
            self.trial_network.set_input(entity_name, entity_name_input)
            save_yaml(data=entity_name_input, file_path=entity_name_input_file_path)
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Created input file for entity {entity_name} to send to Jenkins pipeline")
            entity_name_input_file_content = load_file(file_path=entity_name_input_file_path, mode="rb", encoding=None)
            file = {"FILE": (entity_name_input_file_path, entity_name_input_file_content)}
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Add Jenkins parameters to the pipeline of the {entity_name} entity")
            jenkins_build_job_url = self.jenkins_client.build_job_url(name=self.trial_network.jenkins_deploy_pipeline, parameters=self._jenkins_deployment_parameters(component_type, custom_name, debug))
            response = post(jenkins_build_job_url, auth=(self.jenkins_username, self.jenkins_token), files=file)
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Deployment request code of the {entity_name} entity {response.status_code}")
            if response.status_code != 201:
                raise CustomJenkinsException(f"Error in the response received by Jenkins when trying to deploy the {entity_name} entity", response.status_code)
            next_build_number = self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["nextBuildNumber"]
            while not self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastCompletedBuild"]:
                TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Deploying {entity_name} in {self.trial_network.deployment_site} site")
                sleep(15)
            while next_build_number != self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastCompletedBuild"]["number"]:
                TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Deploying {entity_name} in {self.trial_network.deployment_site} site")
                sleep(15)
            if self.jenkins_client.get_job_info(name=self.trial_network.jenkins_deploy_pipeline)["lastSuccessfulBuild"]["number"] != next_build_number:
                raise CustomJenkinsException(f"Pipeline for the entity {entity_name} has failed", 500)
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Entity {entity_name} successfully deployed")
            sleep(3)
            entity_name_output = TrialNetworkModel.objects(tn_id=self.trial_network.tn_id).first().output
            if entity_name not in entity_name_output:
                raise CustomJenkinsException(f"Callback with the results of the entity {entity_name} not found", 404)
            del deployed_descriptor[entity_name]
            self.trial_network.set_deployed_descriptor(deployed_descriptor)
            self.trial_network.save()
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - End of deployment of entity {entity_name}")
        if not exists_path(path=join_path(f"{self.trial_network.directory_path}", f"{self.trial_network.tn_id}.md")):
            raise CustomJenkinsException(f"File with the report of the trial network {self.trial_network.tn_id} not found", 404)

    def generate_jenkins_destroy_pipeline(self, jenkins_destroy_pipeline: str) -> str:
        """
        Generate destroy pipeline per trial network

        :param jenkins_destroy_pipeline: new name of the destroy pipeline, ``str``
        :return: pipeline use for destroy trial network, ``str``
        :raises CustomJenkinsException:
        """
        if jenkins_destroy_pipeline:
            pipelines = self.get_all_pipelines()
            if jenkins_destroy_pipeline not in pipelines:
                raise CustomJenkinsException(f"The jenkins_destroy_pipeline should be one: {pipelines}", 404)
            if self.jenkins_client.get_job_info(jenkins_destroy_pipeline)["inQueue"]:
                raise CustomJenkinsException(f"The pipeline {jenkins_destroy_pipeline} is currently in use. Try again later", 500)
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Using existing pipeline {jenkins_destroy_pipeline} to destroy the trial network")
            return jenkins_destroy_pipeline

        tn_destroy_pipeline = JenkinsSettings.JENKINS_DESTROY_PIPELINE
        tn_new_destroy_pipeline = f"{tn_destroy_pipeline}_{self.trial_network.tn_id}"
        config = self.jenkins_client.get_job_config(tn_destroy_pipeline)
        config = config.replace(tn_destroy_pipeline, tn_new_destroy_pipeline)
        config = config.replace(f"{tn_new_destroy_pipeline}.groovy", f"{tn_destroy_pipeline}.groovy")
        
        tn_jenkins_destroy_path = f"TNLCM/{tn_new_destroy_pipeline}"
        if tn_jenkins_destroy_path not in self.get_all_pipelines():
            self.jenkins_client.create_job(tn_jenkins_destroy_path, config)
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Created {tn_jenkins_destroy_path} pipeline in Jenkins to destroy the trial network")
        return tn_jenkins_destroy_path

    def _jenkins_destroy_parameters(self) -> dict:
        """
        Function for create dictionary with the parameters for each component to be passed to the destroy pipeline

        :return: dictionary containing mandatory and optional parameters for the Jenkins destroy pipeline, ``dict``
        """
        sorted_descriptor = self.trial_network.sorted_descriptor["trial_network"]
        entities_with_destroy_script = []
        for entity_name, entity_data in sorted_descriptor.items():
            component_type = entity_data["type"]
            component_metadata = self.library_handler.get_component_metadata(component_type)
            if "destroy_script" in component_metadata and component_metadata["destroy_script"]:
                entities_with_destroy_script.append(entity_name)
        return {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "DEPLOYMENT_SITE": self.trial_network.deployment_site,
            "TNLCM_CALLBACK": self.tnlcm_callback,
            # OPTIONAL
            "LIBRARY_URL": self.trial_network.library_https_url,
            "LIBRARY_BRANCH": self.trial_network.library_commit_id,
            "SITES_URL": self.trial_network.sites_https_url,
            "SITES_BRANCH": self.trial_network.sites_commit_id,
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
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Destroying trial network in {self.trial_network.deployment_site} site")
            sleep(15)
        while last_build_number != self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastCompletedBuild"]["number"]:
            TnLogHandler.get_logger(tn_id=self.trial_network.tn_id).info(f"[{self.trial_network.tn_id}] - Destroying trial network in {self.trial_network.deployment_site} site")
            sleep(15)
        if self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["lastSuccessfulBuild"]["number"] != last_build_number:
            raise CustomJenkinsException(f"Pipeline for destroy {self.trial_network.tn_id} trial network has failed", 500)

    def remove_pipeline(self, pipeline_name: str) -> None:
        """
        Remove pipeline in Jenkins

        :param pipeline_name: name of pipeline, ``str`` 
        """
        if pipeline_name not in self.get_all_pipelines():
            raise CustomJenkinsException(f"Pipeline {pipeline_name} not found", 404)
        if pipeline_name != JenkinsSettings.JENKINS_DEPLOY_PIPELINE and pipeline_name != JenkinsSettings.JENKINS_DESTROY_PIPELINE:
            self.jenkins_client.delete_job(pipeline_name)

    def get_all_pipelines(self) -> list[str]:
        """
        Function to get all the pipelines stored in Jenkins

        :return: list with pipelines stored in Jenkins, ``list[str]``
        """
        return [job["fullname"] for job in self.jenkins_client.get_all_jobs() if "fullname" in job and "jobs" not in job]