from time import sleep
from typing import Dict, List, Tuple

from jenkins import Jenkins, JenkinsException

from conf.jenkins import JenkinsSettings
from conf.tnlcm import TnlcmSettings
from core.exceptions.exceptions_handler import JenkinsError
from core.library.library_handler import LibraryHandler
from core.logs.log_handler import TrialNetworkLogger
from core.models.trial_network import TrialNetworkModel
from core.utils.cli import run_command
from core.utils.file import save_yaml_file
from core.utils.os import (
    TEMP_DIRECTORY_PATH,
    join_path,
    remove_file,
)


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

    def clone_pipeline(self, old_name: str, new_name: str) -> Tuple[str, str]:
        """
        Clone pipeline per trial network

        :param old_name: name of the old pipeline, ``str``
        :param new_name: name of the new pipeline, ``str``
        :return: tuple with the name and URL of the new pipeline, ``Tuple[str, str]``
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
        pipeline_url = self.jenkins_client.get_job_info(name=new_name)["url"].replace(
            "http://localhost:8080", JenkinsSettings.JENKINS_URL
        )
        return new_name, pipeline_url

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
        jenkins_deploy_pipeline = self.trial_network.get_jenkins_deploy_pipeline()
        if self.jenkins_client.get_job_info(name=jenkins_deploy_pipeline)["inQueue"]:
            raise JenkinsError(
                message=f"The indicated pipeline {jenkins_deploy_pipeline} is in use and is not available to deploy trial networks",
                status_code=500,
            )
        deployed_descriptor = self.trial_network.to_mongo()["deployed_descriptor"][
            "trial_network"
        ]
        deployed_descriptor_copy = deployed_descriptor.copy()
        for entity_name, entity_data in deployed_descriptor_copy.items():
            component_type = entity_data["type"]
            custom_name = None
            if "name" in entity_data:
                custom_name = entity_data["name"]
            debug = False
            if "debug" in entity_data:
                debug = entity_data["debug"]
            entity_data_input = entity_data["input"]
            entity_input_file_path = join_path(
                TEMP_DIRECTORY_PATH,
                f"{self.trial_network.tn_id}_{entity_name}_input.yaml",
            )
            save_yaml_file(data=entity_data_input, file_path=entity_input_file_path)
            build_params = self.deploy_pipeline_params(
                component_type=component_type, custom_name=custom_name, debug=debug
            )
            build_job_url = self.jenkins_client.build_job_url(
                name=jenkins_deploy_pipeline,
                parameters=build_params,
            )
            next_build_number = self.jenkins_client.get_job_info(
                name=jenkins_deploy_pipeline
            )["nextBuildNumber"]
            stdout, stderr, rc = run_command(
                command=f'curl -w "%{{http_code}}" -X POST "{build_job_url}" -u "{JenkinsSettings.JENKINS_USERNAME}:{JenkinsSettings.JENKINS_TOKEN}" --data-binary "@{entity_input_file_path}"'
            )
            remove_file(path=entity_input_file_path)
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=f"Start deployment of entity {entity_name} in {self.trial_network.deployment_site} site"
            )
            _, status_code = stdout[:-3].strip(), stdout[-3:]
            if status_code != "201":
                raise JenkinsError(
                    message=f"Error in the response received by Jenkins when trying to deploy the {entity_name} entity. Error received: {stderr}. Return code: {rc}",
                    status_code=status_code,
                )
            while (
                not self.jenkins_client.get_job_info(name=jenkins_deploy_pipeline)[
                    "lastBuild"
                ]
                or next_build_number
                != self.jenkins_client.get_job_info(name=jenkins_deploy_pipeline)[
                    "lastBuild"
                ]["number"]
            ):
                sleep(5)
            build_console_num_lines_aux = 0
            while not self.jenkins_client.get_job_info(name=jenkins_deploy_pipeline)[
                "lastCompletedBuild"
            ]:
                build_console_output = self.jenkins_client.get_build_console_output(
                    name=jenkins_deploy_pipeline, number=next_build_number
                )
                build_console_output = (
                    f"Deploying {entity_name} entity in {self.trial_network.deployment_site} site\n"
                    "------------------------------------------------------------------------------------------------------------------\n"
                    f"{build_console_output}"
                    "------------------------------------------------------------------------------------------------------------------"
                )
                build_console_num_lines = build_console_output.count("\n")
                TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                    message=build_console_output,
                    lines_to_remove=build_console_num_lines_aux,
                )
                build_console_num_lines_aux = build_console_num_lines
                sleep(10)
            while (
                next_build_number
                != self.jenkins_client.get_job_info(name=jenkins_deploy_pipeline)[
                    "lastCompletedBuild"
                ]["number"]
            ):
                build_console_output = self.jenkins_client.get_build_console_output(
                    name=jenkins_deploy_pipeline, number=next_build_number
                )
                build_console_output = (
                    f"Deploying {entity_name} entity in {self.trial_network.deployment_site} site\n"
                    "------------------------------------------------------------------------------------------------------------------\n"
                    f"{build_console_output}"
                    "------------------------------------------------------------------------------------------------------------------"
                )
                build_console_num_lines = build_console_output.count("\n")
                TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                    message=build_console_output,
                    lines_to_remove=build_console_num_lines_aux,
                )
                build_console_num_lines_aux = build_console_num_lines
                sleep(10)
            build_console_output = self.jenkins_client.get_build_console_output(
                name=jenkins_deploy_pipeline, number=next_build_number
            )
            build_console_output = (
                f"Pipeline response for the deployment of the entity {entity_name} in {self.trial_network.deployment_site} site\n"
                "------------------------------------------------------------------------------------------------------------------\n"
                f"{build_console_output}"
                "------------------------------------------------------------------------------------------------------------------"
            )
            if (
                self.jenkins_client.get_job_info(name=jenkins_deploy_pipeline)[
                    "lastSuccessfulBuild"
                ]["number"]
                != next_build_number
            ):
                raise JenkinsError(
                    message=(f"{build_console_output}"),
                    status_code=500,
                )
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=build_console_output,
                lines_to_remove=build_console_num_lines_aux,
            )
            self.trial_network.set_jenkins_deploy_build(
                build_name=entity_name,
                build_number=next_build_number,
                build_params=build_params,
                build_console=build_console_output,
                build_file=entity_data_input,
            )
            del deployed_descriptor[entity_name]
            self.trial_network.set_deployed_descriptor(
                deployed_descriptor=deployed_descriptor
            )
            self.trial_network.save()

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
        jenkins_destroy_pipeline = self.trial_network.get_jenkins_destroy_pipeline()
        if self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)["inQueue"]:
            raise JenkinsError(
                message=f"The indicated pipeline {jenkins_destroy_pipeline} is in use and is not available to destroy trial networks",
                status_code=500,
            )
        next_build_number = self.jenkins_client.get_job_info(
            name=jenkins_destroy_pipeline
        )["nextBuildNumber"]
        build_params = self.destroy_pipeline_params()
        self.jenkins_client.build_job(
            name=jenkins_destroy_pipeline,
            parameters=build_params,
            token=JenkinsSettings.JENKINS_TOKEN,
        )
        while (
            not self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)[
                "lastBuild"
            ]
            or next_build_number
            != self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)[
                "lastBuild"
            ]["number"]
        ):
            sleep(5)
        build_console_num_lines_aux = 0
        while not self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)[
            "lastCompletedBuild"
        ]:
            build_console_output = self.jenkins_client.get_build_console_output(
                name=jenkins_destroy_pipeline, number=next_build_number
            )
            build_console_output = (
                f"Destroying trial network in {self.trial_network.deployment_site} site\n"
                "------------------------------------------------------------------------------------------------------------------\n"
                f"{build_console_output}"
                "------------------------------------------------------------------------------------------------------------------"
            )
            build_console_num_lines = build_console_output.count("\n")
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=build_console_output,
                lines_to_remove=build_console_num_lines_aux,
            )
            build_console_num_lines_aux = build_console_num_lines
            sleep(10)
        while (
            next_build_number
            != self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)[
                "lastCompletedBuild"
            ]["number"]
        ):
            build_console_output = self.jenkins_client.get_build_console_output(
                name=jenkins_destroy_pipeline, number=next_build_number
            )
            build_console_output = (
                f"Destroying trial network in {self.trial_network.deployment_site} site\n"
                "------------------------------------------------------------------------------------------------------------------\n"
                f"{build_console_output}"
                "------------------------------------------------------------------------------------------------------------------"
            )
            build_console_num_lines = build_console_output.count("\n")
            TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
                message=build_console_output,
                lines_to_remove=build_console_num_lines_aux,
            )
            build_console_num_lines_aux = build_console_num_lines
            sleep(10)
        build_console_output = self.jenkins_client.get_build_console_output(
            name=jenkins_destroy_pipeline, number=next_build_number
        )
        build_console_output = (
            f"Pipeline response for the destroy of trial network in {self.trial_network.deployment_site} site\n"
            "------------------------------------------------------------------------------------------------------------------\n"
            f"{build_console_output}"
            "------------------------------------------------------------------------------------------------------------------"
        )
        if (
            self.jenkins_client.get_job_info(name=jenkins_destroy_pipeline)[
                "lastSuccessfulBuild"
            ]["number"]
            != next_build_number
        ):
            raise JenkinsError(
                message=(f"{build_console_output}"),
                status_code=500,
            )
        TrialNetworkLogger(tn_id=self.trial_network.tn_id).info(
            message=build_console_output,
            lines_to_remove=build_console_num_lines_aux,
        )
        self.trial_network.set_jenkins_destroy_build(
            build_number=str(next_build_number),
            build_params=build_params,
            build_console=build_console_output,
        )
        self.trial_network.save()

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
        if (
            pipeline_name in self.get_all_pipelines()
            and pipeline_name != JenkinsSettings.JENKINS_DEPLOY_PIPELINE
            and pipeline_name != JenkinsSettings.JENKINS_DESTROY_PIPELINE
        ):
            self.jenkins_client.delete_job(name=pipeline_name)

    # FEATURE: deploy component
    # def deploy_component(
    #     self, tn_id: str, pipeline_name: str, build_params: Dict, file
    # ) -> None:
    #     """
    #     Deploy component in Jenkins

    #     :param tn_id: trial network identifier, ``str``
    #     :param pipeline_name: name of pipeline, ``str``
    #     :param build_params: dictionary with the parameters for the Jenkins deployment pipeline, ``Dict``
    #     :param file: file to be passed to the Jenkins deployment pipeline
    #     :raises JenkinsError:
    #     """
    #     if "CUSTOM_NAME" in build_params:
    #         entity_name = (
    #             f"{build_params['CUSTOM_NAME']}-{build_params['COMPONENT_TYPE']}"
    #         )
    #     else:
    #         entity_name = build_params["COMPONENT_TYPE"]
    #     TrialNetworkLogger(tn_id=tn_id).info(
    #         message=f"Start deployment of entity {entity_name} using the pipeline {pipeline_name}"
    #     )
    #     next_build_number = self.jenkins_client.get_job_info(name=pipeline_name)[
    #         "nextBuildNumber"
    #     ]
    #     build_job_url = self.jenkins_client.build_job_url(
    #         name=pipeline_name,
    #         parameters=build_params,
    #     )
    #     stdout, stderr, rc = run_command(
    #         command=f'curl -w "%{{http_code}}" -X POST "{build_job_url}" -u "{JenkinsSettings.JENKINS_USERNAME}:{JenkinsSettings.JENKINS_TOKEN}" --data-binary "@{file}"'
    #     )
    #     _, status_code = stdout[:-3].strip(), stdout[-3:]
    #     if status_code != "201":
    #         raise JenkinsError(
    #             message=f"Error in the response received by Jenkins when trying to deploy the entity {entity_name}. Error received: {stderr}. Return code: {rc}",
    #             status_code=status_code,
    #         )
    #     while (
    #         not self.jenkins_client.get_job_info(name=pipeline_name)["lastBuild"]
    #         or next_build_number
    #         != self.jenkins_client.get_job_info(name=pipeline_name)["lastBuild"][
    #             "number"
    #         ]
    #     ):
    #         sleep(5)
    #     build_console_num_lines_aux = 0
    #     while not self.jenkins_client.get_job_info(name=pipeline_name)[
    #         "lastCompletedBuild"
    #     ]:
    #         build_console_output = self.jenkins_client.get_build_console_output(
    #             name=pipeline_name, number=next_build_number
    #         )
    #         build_console_output = (
    #             f"Deploying entity {entity_name}\n"
    #             "------------------------------------------------------------------------------------------------------------------\n"
    #             f"{build_console_output}"
    #             "------------------------------------------------------------------------------------------------------------------"
    #         )
    #         build_console_num_lines = build_console_output.count("\n")
    #         TrialNetworkLogger(tn_id=tn_id).info(
    #             message=build_console_output,
    #             lines_to_remove=build_console_num_lines_aux,
    #         )
    #         build_console_num_lines_aux = build_console_num_lines
    #         sleep(10)
    #     while (
    #         next_build_number
    #         != self.jenkins_client.get_job_info(name=pipeline_name)[
    #             "lastCompletedBuild"
    #         ]["number"]
    #     ):
    #         build_console_output = self.jenkins_client.get_build_console_output(
    #             name=pipeline_name, number=next_build_number
    #         )
    #         build_console_output = (
    #             f"Deploying entity {entity_name}\n"
    #             "------------------------------------------------------------------------------------------------------------------\n"
    #             f"{build_console_output}"
    #             "------------------------------------------------------------------------------------------------------------------"
    #         )
    #         build_console_num_lines = build_console_output.count("\n")
    #         TrialNetworkLogger(tn_id=tn_id).info(
    #             message=build_console_output,
    #             lines_to_remove=build_console_num_lines_aux,
    #         )
    #         build_console_num_lines_aux = build_console_num_lines
    #         sleep(10)
    #     build_console_output = self.jenkins_client.get_build_console_output(
    #         name=pipeline_name, number=next_build_number
    #     )
    #     build_console_output = (
    #         f"Pipeline response for the deployment of the entity {entity_name} in {self.trial_network.deployment_site} site\n"
    #         "------------------------------------------------------------------------------------------------------------------\n"
    #         f"{build_console_output}"
    #         "------------------------------------------------------------------------------------------------------------------"
    #     )
    #     if (
    #         self.jenkins_client.get_job_info(name=pipeline_name)["lastSuccessfulBuild"][
    #             "number"
    #         ]
    #         != next_build_number
    #     ):
    #         raise JenkinsError(
    #             message=(f"{build_console_output}"),
    #             status_code=500,
    #         )
    #     TrialNetworkLogger(tn_id=tn_id).info(
    #         message=build_console_output,
    #         lines_to_remove=build_console_num_lines_aux,
    #     )
