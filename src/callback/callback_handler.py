import os

from json import dump
from base64 import b64decode

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import KeyNotFoundError, CustomUnicodeDecodeError

REPORT_DIRECTORY = os.path.join(os.getcwd(), "src", "callback", "reports")

class CallbackHandler:

    def __init__(self, data):
        self.data = data
        os.makedirs(REPORT_DIRECTORY, exist_ok=True)

    def save_decoded_results(self):
        """Store decoded deployment information of each component received by Jenkins"""
        try:
            log_handler.info("Saving entity deployment results received by Jenkins")
            missing_keys = [key for key in ["tn_id", "library_component_name", "entity_name", "success", "markdown", "output"] if key not in self.data]
            if missing_keys:
                raise KeyNotFoundError(f"Missing keys: {', '.join(missing_keys)}", 400)
            decoded_data = {}
            for key_data, value_data in self.data.items():
                if key_data == "output":
                    decoded_output = {}
                    for key_output, value_output in value_data.items:
                        decoded_output[key_output] = b64decode(value_output).decode("utf-8")
                    decoded_data[key_data] = decoded_output
                else:
                    decoded_data[key_data] = b64decode(value_data).decode("utf-8")
            
            entity_file_name = decoded_data["tn_id"] + "-" + decoded_data["library_component_name"] + "-" + decoded_data["entity_name"] + ".json"
            path_entity_file_name = os.path.join(REPORT_DIRECTORY, entity_file_name)
            
            with open(path_entity_file_name, "w") as entity_result:
                dump(decoded_data, entity_result)

            log_handler.info(f"Information of the '{decoded_data["entity_name"]}' entity stored in the file '{entity_file_name}' located in the path '{path_entity_file_name}'")

            report_trial_network_name = decoded_data["tn_id"] + ".md"
            path_report_trial_network = os.path.join(REPORT_DIRECTORY, report_trial_network_name)

            with open(path_report_trial_network, "a") as markdown_file:
                markdown_file.write(decoded_data["markdown"])

            log_handler.info(f"'markdown' of the '{decoded_data["entity_name"]}' entity stored in the report file '{report_trial_network_name}' located in the path '{path_report_trial_network}'")
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 401)