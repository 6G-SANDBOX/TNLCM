import os

from json import dump
from yaml import safe_load, YAMLError
from base64 import b64decode

from conf import SixGLibrarySettings
from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import KeyNotFoundError, CustomUnicodeDecodeError, InvalidContentFileError, CustomFileNotFoundError, KeyNotFoundError

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
REPORT_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "reports")
SIXG_LIBRARY_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "..", "sixg_library")
JENKINS_RESULT_KEYS = ["tn_id", "component_type", "custom_name", "success", "output", "markdown"]

class CallbackHandler:

    def __init__(self, data=None, trial_network=None):
        """Constructor"""
        self.data = data
        self.trial_network = trial_network
        os.makedirs(REPORT_DIRECTORY, exist_ok=True)

    def save_pipeline_results(self):
        """Save decoded deployment information of each component received by Jenkins"""
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
            
            if not self._is_output_correct(output_jenkins, component_type):
                raise InvalidContentFileError("Output received by Jenkins does not match output from the 6G-Library", 500)
            
            entity_file_name = f"{tn_id}-{component_type}-{custom_name}.json" if custom_name != "None" else f"{tn_id}-{component_type}.json"
            path_entity_file_name = os.path.join(REPORT_DIRECTORY, entity_file_name)
            
            with open(path_entity_file_name, "w") as entity_file:
                dump(decoded_data, entity_file)
            
            entity = f"{component_type}-{custom_name}" if custom_name != "None" else component_type
            log_handler.info(f"Information of the '{entity}' entity save in the file '{entity_file_name}' located in the path '{path_entity_file_name}'")

            report_trial_network_name = f"{tn_id}.md"
            path_report_trial_network = os.path.join(REPORT_DIRECTORY, report_trial_network_name)

            with open(path_report_trial_network, "a") as report_trial_network:
                report_trial_network.write(markdown)

            log_handler.info(f"'Markdown' of the '{entity}' entity save in the report file '{report_trial_network_name}' located in the path '{path_report_trial_network}'")               
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 401)

    def _is_output_correct(self, output_jenkins, component_type):
        """Return true if output received by Jenkins is the same as the output of the 6G-Library"""
        log_handler.info("Check if output received by Jenkins is the same as the output of the 6G-Library")
        public_file = os.path.join(SIXG_LIBRARY_DIRECTORY, SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME, component_type, ".tnlcm", "public.yaml")
        if not os.path.exists(public_file):
            raise CustomFileNotFoundError(f"File '{public_file}' not found", 404)
        with open(public_file, "rt", encoding="utf8") as file:
            try:
                public_data = safe_load(file)
            except YAMLError:
                raise InvalidContentFileError(f"File '{public_file}' is not parsed correctly", 422)
        if "output" not in public_data:
            raise KeyNotFoundError(f"Key 'output' is missing in the file located in the path '{public_file}'", 404)
        output_component = public_data["output"]
        return set(output_jenkins.keys()) == set(output_component.keys())

    def get_path_report_trial_network(self):
        """Return path where report of trial network is stored"""
        path_report_trial_network = os.path.join(REPORT_DIRECTORY, f"{self.trial_network.tn_id}.md")
        if not os.path.exists(path_report_trial_network):
            raise CustomFileNotFoundError("Trial network report file has not been found", 404)
        return path_report_trial_network
    
    def exists_path_entity_trial_network(self, entity_name):
        """Return true if exists entity file with information received by Jenkins"""
        log_handler.info(f"Check whether the file of the '{entity_name}' entity has been created.")
        path_entity_trial_network = os.path.join(REPORT_DIRECTORY, f"{self.trial_network.tn_id}-{entity_name}.json")
        return os.path.exists(path_entity_trial_network)