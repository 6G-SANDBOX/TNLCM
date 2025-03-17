from time import sleep
from typing import Dict, List

from jenkins import Jenkins, JenkinsException

from conf.jenkins import JenkinsSettings
from conf.tnlcm import TnlcmSettings
from core.exceptions.exceptions_handler import JenkinsError
from core.library.library_handler import LibraryHandler
from core.logs.log_handler import TrialNetworkLogger
from core.models.trial_network import TrialNetworkModel
from core.utils.cli import run_command
from core.utils.file import save_yaml_file
from core.utils.os import is_file, join_path


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
        :raises JenkinsError:
        """
        self.trial_network = trial_network
        self.library_handler = library_handler
        try:
            self.jenkins_client = Jenkins(
                url=JenkinsSettings.JENKINS_URL,
                username=JenkinsSettings.JENKINS_USERNAME,
                password=JenkinsSettings.JENKINS_PASSWORD,
            )
            self.jenkins_client.get_whoami()
        except JenkinsException:
            raise JenkinsError(
                message=f"Failed when trying to connect to Jenkins. Check the connection settings. Configuration used: {JenkinsSettings.JENKINS_URL}, {JenkinsSettings.JENKINS_USERNAME} and {JenkinsSettings.JENKINS_PASSWORD}",
                status_code=500,
            )

    def clone_pipeline(self, old_name: str, new_name: str) -> str:
        """
        Clone pipeline per trial network

        :param old_name: name of the old pipeline, ``str``
        :param new_name: name of the new pipeline, ``str``
        :return: name of the new pipeline, ``str``
        :raises JenkinsError:
        """
        pipelines = self.get_all_pipelines()
        if old_name not in pipelines:
            raise JenkinsError(
                message=f"Failed to create the new pipeline {new_name} using the old pipeline {old_name}. The old pipeline does not exist",
                status_code=404,
            )
        if not self.is_tnlcm_dir():
            self.jenkins_client.create_folder(
                folder_name=JenkinsSettings.JENKINS_TNLCM_DIRECTORY
            )
        if new_name not in pipelines:
            config = self.jenkins_client.get_job_config(name=old_name)
            config = config.replace(old_name, new_name)
            config = config.replace(f"{new_name}.groovy", f"{old_name}.groovy")
            self.jenkins_client.create_job(name=new_name, config_xml=config)
        TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
            message=f"Pipeline {new_name} available in Jenkins for the trial network"
        )
        return new_name

    def deploy_pipeline_params(
        self, component_type: str, custom_name: str, debug: str
    ) -> Dict:
        """
        Function for create dictionary with the parameters for each component to be passed to the deployment pipeline

        :param component_type: type part of the descriptor file, ``str``
        :param custom_name: name part of the descriptor file, ``str``
        :param debug: debug part of the descriptor file (optional), ``str``
        :return: dictionary containing mandatory and optional parameters for the Jenkins deployment pipeline, ``Dict``
        """
        parameters = {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "COMPONENT_TYPE": component_type,
            "DEPLOYMENT_SITE": self.trial_network.deployment_site,
            "TNLCM_CALLBACK": TnlcmSettings.TNLCM_CALLBACK,
            # OPTIONAL
            "LIBRARY_URL": self.trial_network.library_https_url,
            "LIBRARY_BRANCH": self.trial_network.library_commit_id,
            "SITES_URL": self.trial_network.sites_https_url,
            "SITES_BRANCH": self.trial_network.sites_commit_id,
            "DEBUG": debug,
        }
        if custom_name:
            parameters["CUSTOM_NAME"] = custom_name
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"Declare parameters for the deployment of the entity name {custom_name}"
            )
        else:
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"Declare parameters for the deployment of the component type {component_type}"
            )
        return parameters

    def deploy_trial_network(self) -> None:
        """
        Trial network deploy

        :raises JenkinsError:
        """
        deployed_descriptor = self.trial_network.to_mongo()["deployed_descriptor"][
            "trial_network"
        ]
        deployed_descriptor_copy = deployed_descriptor.copy()
        if self.jenkins_client.get_job_info(
            name=self.trial_network.jenkins_deploy_pipeline
        )["inQueue"]:
            raise JenkinsError(
                message=f"The indicated pipeline {self.trial_network.jenkins_deploy_pipeline} is in use and is not available to deploy trial networks",
                status_code=500,
            )
        job_info = self.jenkins_client.get_job_info(
            name=self.trial_network.jenkins_deploy_pipeline
        )["url"]
        job_info = job_info.replace(
            "http://localhost:8080", JenkinsSettings.JENKINS_URL
        )
        TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
            message=f"To see the logs of the deployment of the trial network in Jenkins, access the following link: {job_info}"
        )
        for entity_name, entity_data in deployed_descriptor_copy.items():
            component_type = entity_data["type"]
            custom_name = None
            if "name" in entity_data:
                custom_name = entity_data["name"]
            debug = False
            if "debug" in entity_data:
                debug = entity_data["debug"]
            entity_input_file_path = join_path(
                self.trial_network.directory_path,
                "input",
                f"{self.trial_network.tn_id}-{entity_name}.yaml",
            )
            entity_data_input = entity_data["input"]
            self.trial_network.set_input(
                entity_name=entity_name, entity_data_input=entity_data_input
            )
            save_yaml_file(data=entity_data_input, file_path=entity_input_file_path)
            build_job_url = self.jenkins_client.build_job_url(
                name=self.trial_network.jenkins_deploy_pipeline,
                parameters=self.deploy_pipeline_params(
                    component_type=component_type, custom_name=custom_name, debug=debug
                ),
            )
            stdout, stderr, rc = run_command(
                command=f'curl -w "%{{http_code}}" -X POST "{build_job_url}" -u "{JenkinsSettings.JENKINS_USERNAME}:{JenkinsSettings.JENKINS_TOKEN}" --data-binary "@{entity_input_file_path}"'
            )
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"Start deployment of entity {entity_name}"
            )
            _, status_code = stdout[:-3].strip(), stdout[-3:]
            if status_code != "201":
                raise JenkinsError(
                    message=f"Error in the response received by Jenkins when trying to deploy the {entity_name} entity. Error received: {stderr}. Return code: {rc}",
                    status_code=status_code,
                )
            next_build_number = self.jenkins_client.get_job_info(
                name=self.trial_network.jenkins_deploy_pipeline
            )["nextBuildNumber"]
            while not self.jenkins_client.get_job_info(
                name=self.trial_network.jenkins_deploy_pipeline
            )["lastCompletedBuild"]:
                TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                    message=f"Deploying {entity_name} entity in {self.trial_network.deployment_site} site"
                )
                sleep(15)
            while (
                next_build_number
                != self.jenkins_client.get_job_info(
                    name=self.trial_network.jenkins_deploy_pipeline
                )["lastCompletedBuild"]["number"]
            ):
                TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                    message=f"Deploying {entity_name} entity in {self.trial_network.deployment_site} site"
                )
                sleep(15)
            if (
                self.jenkins_client.get_job_info(
                    name=self.trial_network.jenkins_deploy_pipeline
                )["lastSuccessfulBuild"]["number"]
                != next_build_number
            ):
                raise JenkinsError(
                    message=f"Pipeline {self.trial_network.jenkins_destroy_pipeline} failed when trying to deploy the {entity_name} entity in {self.trial_network.deployment_site} site. Check the logs",
                    status_code=500,
                )
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"Entity {entity_name} successfully deployed"
            )
            sleep(3)
            entity_output = (
                TrialNetworkModel.objects(tn_id=self.trial_network.tn_id).first().output
            )
            if entity_name not in entity_output:
                raise JenkinsError(
                    message=f"Callback with the output of the entity {entity_name} was not received from Jenkins",
                    status_code=404,
                )
            del deployed_descriptor[entity_name]
            self.trial_network.set_deployed_descriptor(
                deployed_descriptor=deployed_descriptor
            )
            self.trial_network.save()
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"End of deployment of entity {entity_name}"
            )
        if not is_file(
            path=join_path(
                f"{self.trial_network.directory_path}", f"{self.trial_network.tn_id}.md"
            )
        ):
            raise JenkinsError(
                message=f"File with the report of the trial network {self.trial_network.tn_id} not found",
                status_code=404,
            )

    def destroy_pipeline_params(self) -> Dict:
        """
        Function for create dictionary with the parameters for each component to be passed to the destroy pipeline

        :return: dictionary containing mandatory and optional parameters for the Jenkins destroy pipeline, ``Dict``
        """
        sorted_descriptor = self.trial_network.sorted_descriptor["trial_network"]
        entities_with_destroy_script = []
        for entity_name, entity_data in sorted_descriptor.items():
            component_type = entity_data["type"]
            component_metadata = self.library_handler.get_component_metadata(
                component_name=component_type
            )
            if (
                "destroy_script" in component_metadata
                and component_metadata["destroy_script"]
            ):
                entities_with_destroy_script.append(entity_name)
        return {
            # MANDATORY
            "TN_ID": self.trial_network.tn_id,
            "DEPLOYMENT_SITE": self.trial_network.deployment_site,
            "TNLCM_CALLBACK": TnlcmSettings.TNLCM_CALLBACK,
            # OPTIONAL
            "LIBRARY_URL": self.trial_network.library_https_url,
            "LIBRARY_BRANCH": self.trial_network.library_commit_id,
            "SITES_URL": self.trial_network.sites_https_url,
            "SITES_BRANCH": self.trial_network.sites_commit_id,
            # "SCRIPTED_DESTROY_COMPONENTS": entities_with_destroy_script
            # "DEBUG": true
        }

    def destroy_trial_network(self) -> None:
        """
        Trial network destroy starts

        :raises JenkinsError:
        """
        job_info = self.jenkins_client.get_job_info(
            name=self.trial_network.jenkins_destroy_pipeline
        )["url"]
        job_info = job_info.replace(
            "http://localhost:8080", JenkinsSettings.JENKINS_URL
        )
        TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
            message=f"To see the logs of the destruction of the trial network in Jenkins, access the following link: {job_info}"
        )
        build_job_url = self.jenkins_client.build_job_url(
            name=self.trial_network.jenkins_destroy_pipeline,
            parameters=self.destroy_pipeline_params(),
        )
        self.jenkins_client.build_job(
            name=self.trial_network.jenkins_destroy_pipeline,
            parameters=self.destroy_pipeline_params(),
            token=JenkinsSettings.JENKINS_TOKEN,
        )
        last_build_number = self.jenkins_client.get_job_info(
            name=self.trial_network.jenkins_destroy_pipeline
        )["nextBuildNumber"]
        while not self.jenkins_client.get_job_info(
            name=self.trial_network.jenkins_destroy_pipeline
        )["lastCompletedBuild"]:
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"Destroying trial network in {self.trial_network.deployment_site} site"
            )
            sleep(15)
        while (
            last_build_number
            != self.jenkins_client.get_job_info(
                name=self.trial_network.jenkins_destroy_pipeline
            )["lastCompletedBuild"]["number"]
        ):
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"Destroying trial network in {self.trial_network.deployment_site} site"
            )
            sleep(15)
        if (
            self.jenkins_client.get_job_info(
                name=self.trial_network.jenkins_destroy_pipeline
            )["lastSuccessfulBuild"]["number"]
            != last_build_number
        ):
            raise JenkinsError(
                message=f"Pipeline {self.trial_network.jenkins_destroy_pipeline} failed when trying to destroy the trial network in {self.trial_network.deployment_site} site. To see the logs, access the following link: {build_job_url}",
                status_code=500,
            )
        TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
            message="Trial network successfully destroyed"
        )

    def get_all_pipelines(self) -> List[str]:
        """
        Function to get all the pipelines stored in Jenkins

        :return: list with pipelines stored in Jenkins, ``List[str]``
        """
        return [
            job["fullname"]
            for job in self.jenkins_client.get_all_jobs()
            if "fullname" in job and "jobs" not in job
        ]

    def is_tnlcm_dir(self) -> bool:
        """
        Check if the TNLCM directory exists in Jenkins

        :return: True if directory exists, False otherwise, ``bool``
        """
        return any(
            job["name"] == JenkinsSettings.JENKINS_TNLCM_DIRECTORY
            for job in self.jenkins_client.get_jobs(folder_depth=0)
        )

    def remove_pipeline(self, pipeline_name: str) -> None:
        """
        Remove pipeline in Jenkins

        :param pipeline_name: name of pipeline, ``str``
        """
        if pipeline_name not in self.get_all_pipelines():
            raise JenkinsError(
                message=f"Failed to remove the pipeline {pipeline_name}. The pipeline does not exist in Jenkins",
                status_code=404,
            )
        if (
            pipeline_name != JenkinsSettings.JENKINS_DEPLOY_PIPELINE
            and pipeline_name != JenkinsSettings.JENKINS_DESTROY_PIPELINE
        ):
            self.jenkins_client.delete_job(name=pipeline_name)
