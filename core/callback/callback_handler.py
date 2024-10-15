import os

from json import dump
from yaml import safe_load, YAMLError
from base64 import b64decode

from conf import SixGLibrarySettings, TnlcmSettings
from core.logs.log_handler import log_handler
from core.models.trial_network import TrialNetworkModel
from core.exceptions.exceptions_handler import KeyNotFoundError, CustomUnicodeDecodeError, InvalidContentFileError, CustomFileNotFoundError, KeyNotFoundError

JENKINS_RESULT_KEYS = ["tn_id", "component_type", "custom_name", "success", "output", "markdown"]

class CallbackHandler:

    def __init__(
        self, 
        data: dict = None, 
        trial_network: TrialNetworkModel = None
    ) -> None:
        """
        Constructor

        :param data: result sent by Jenkins after the deployment of a component, ``dict``
        :param trial_network: model of the trial network to be deployed, ``TrialNetworkModel``
        """
        self.data = data
        self.trial_network = trial_network

    def save_pipeline_results(self) -> None:
        """
        Save decoded deployment information of each component received by Jenkins
        
        :raises KeyNotFoundError: if any required key is missing in the received data (error code 400)
        :raises InvalidContentFileError: if the output from Jenkins does not match the expected output defined in 6G-Library (error code 500)
        :raises CustomUnicodeDecodeError: if there is a Unicode decoding error during data processing (error code 401)
        """
        try:
            log_handler.info("Save entity deployment results received by Jenkins")
            missing_keys = [key for key in JENKINS_RESULT_KEYS if key not in self.data]
            if missing_keys:
                raise KeyNotFoundError(f"Missing keys: {', '.join(missing_keys)}", 400)
            decoded_data = {}
            for key_data, value_data in self.data.items():
                if key_data == "output":
                    decoded_output = {}
                    for key_output, value_output in value_data.items():
                        decoded_output[key_output] = b64decode(value_output).decode("utf-8")
                    decoded_data[key_data] = decoded_output
                elif key_data == "success":
                    decoded_data[key_data] = value_data
                else:
                    decoded_data[key_data] = b64decode(value_data).decode("utf-8")
            
            custom_name = decoded_data["custom_name"]
            component_type = decoded_data["component_type"]
            tn_id = decoded_data["tn_id"]
            success = decoded_data["success"]
            output_jenkins = decoded_data["output"]
            markdown = decoded_data["markdown"]
            
            if success == "true":
                if not self._is_output_correct(tn_id, output_jenkins, component_type):
                    raise InvalidContentFileError("Output received by Jenkins does not match output from the 6G-Library", 500)
            
            entity_name_json = f"{tn_id}-{component_type}-{custom_name}.json" if custom_name != "None" else f"{tn_id}-{component_type}.json"
            path_entity_name_json = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, tn_id, entity_name_json)
            
            with open(path_entity_name_json, "w") as entity_file:
                dump(decoded_data, entity_file)
            
            entity_name = f"{component_type}-{custom_name}" if custom_name != "None" else component_type
            log_handler.info(f"Information of the '{entity_name}' entity save in the file '{entity_name_json}' located in the path '{path_entity_name_json}'")

            tn_report_markdown = f"{tn_id}.md"
            path_tn_report_markdown = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, tn_id, tn_report_markdown)

            with open(path_tn_report_markdown, "a") as tn_report:
                tn_report.write(markdown + "\n")

            log_handler.info(f"'Markdown' of the '{entity_name}' entity save in the report file '{tn_report_markdown}' located in the path '{path_tn_report_markdown}'")               
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 401)

    def _is_output_correct(self, tn_id: str, output_jenkins: dict, component_type: dict) -> bool:
        """
        Function to check that the output received by Jenkins is the same as the output defined in 6G-Library
        
        :param tn_id: trial network identifier, ``str``
        :param output_jenkins: data received by Jenkins, ``dict``
        :param component_type: data expected to be received indicated by the 6G-Library, ``dict``
        :return: True if output received by Jenkins is the same as the output defined in 6G-Library. Otherwise False, ``bool``
        :raises CustomFileNotFoundError: if the public file for the component type is not found (error code 404)
        :raises InvalidContentFileError: if the public file is not parsed correctly (error code 422)
        :raises KeyNotFoundError: if the 'output' key is missing from the public file (error code 404)
        """
        log_handler.info("Check if output received by Jenkins is the same as the output of the 6G-Library")
        public_file = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, tn_id, SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME, component_type, ".tnlcm", "public.yaml")
        if not os.path.exists(public_file):
            raise CustomFileNotFoundError(f"File '{public_file}' not found", 404)
        with open(public_file, "rt", encoding="utf8") as file:
            try:
                public_data = safe_load(file)
            except YAMLError:
                raise InvalidContentFileError(f"File '{public_file}' is not parsed correctly", 422)
        if "output" not in public_data:
            raise KeyNotFoundError(f"Key 'output' is missing in the file located in the path '{public_file}'", 404)
        output_library = public_data["output"]
        if output_library and len(component_type) > 0 and output_jenkins and len(output_jenkins) > 0:
            return set(output_jenkins.keys()) == set(output_library.keys())
        if not output_library and len(output_jenkins) == 0:
            return True
        return False

    def get_path_tn_report_markdown(self) -> str:
        """
        Function to check if the Trial Network report has been saved

        :return: path where report of trial network is stored, ``str``
        :raises CustomFileNotFoundError: if the trial network report file is not found (error code 404)
        """
        path_tn_report_markdown = os.path.join(f"{self.trial_network.tn_folder}", f"{self.trial_network.tn_id}.md")
        if not os.path.exists(path_tn_report_markdown):
            raise CustomFileNotFoundError("Trial network report file has not been found", 404)
        return path_tn_report_markdown
    
    def exists_path_entity_name_json(self, entity_name: str) -> bool:
        """
        Function to check if exists entity file with information received by Jenkins

        :param entity_name: component type-name, ``str``
        :return: True if the entity file exists. Otherwise False, ``bool``
        """
        log_handler.info(f"Check whether the file of the '{entity_name}' entity has been created")
        return os.path.exists(os.path.join(f"{self.trial_network.tn_folder}", f"{self.trial_network.tn_id}-{entity_name}.json"))