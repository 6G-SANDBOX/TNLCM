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
        """Store decoded deployment information of each component received by jenkins"""
        try:
            log_handler.info("Saving entity deployment results received by jenkins")
            missing_keys = [key for key in ["tn_id", "library_component_name", "entity_name", "result_msg"] if key not in self.data]
            if missing_keys:
                raise KeyNotFoundError(f"Missing keys: {", ".join(missing_keys)}", 400)
            if "kubeconfig" in self.data:
                self.data["kubeconfig"] = b64decode(self.data["kubeconfig"]).decode("utf-8")
            self.data["result_msg"] = b64decode(self.data["result_msg"]).decode("utf-8")
            entity_file_name = self.data["tn_id"] + "-" + self.data["library_component_name"] + "-" + self.data["entity_name"] + ".json"
            path_entity_file_name = os.path.join(REPORT_DIRECTORY, entity_file_name)
            with open(path_entity_file_name, "w") as entity_result:
                dump(self.data, entity_result)
            result_msg = self.data["result_msg"]
            report_trial_network_name = self.data["tn_id"] + ".md"
            path_report_trial_network = os.path.join(REPORT_DIRECTORY, report_trial_network_name)
            with open(path_report_trial_network, "a") as result_msg_file:
                result_msg_file.write(result_msg)
            log_handler.info("Saved entity deployment information")
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 500)