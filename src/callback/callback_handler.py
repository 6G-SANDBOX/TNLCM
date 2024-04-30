import os

from json import dump
from base64 import b64decode

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import KeyNotFoundError, CustomUnicodeDecodeError

REPORT_DIRECTORY = os.path.join(os.getcwd(), "src", "callback", "reports")

class CallbackHandler:

    def __init__(self, data):
        self.data = data

    def save_decoded_information(self):
        """Store decoded deployment information of each component received by jenkins"""
        try:
            log_handler.info("Saving entity deployment results received by jenkins")
            if "tn_id" not in self.data or "library_component_name" not in self.data or "entity_name" not in self.data:
                raise KeyNotFoundError(f"The 'tn_id', 'library_component_name' or 'entity_name' key has not been received by Jenkins", 400)
            if "result_msg" not in self.data:
                raise KeyNotFoundError(f"The 'result_msg' key has not been received by Jenkins", 400)
            if "kubeconfig" in self.data:
                self.data["kubeconfig"] = b64decode(self.data["kubeconfig"]).decode("utf-8")
            if not os.path.exists(REPORT_DIRECTORY):
                os.makedirs(REPORT_DIRECTORY)
            self.data["result_msg"] = b64decode(self.data["result_msg"]).decode("utf-8")
            entity_file_name = self.data["tn_id"] + "-" + self.data["library_component_name"] + "-" + self.data["entity_name"] + ".json"
            path_entity_file_name = os.path.join(REPORT_DIRECTORY, entity_file_name)
            with open(path_entity_file_name, "w") as decoded_information_file:
                dump(self.data, decoded_information_file)
            result_msg = self.data["result_msg"]
            report_trial_network_name = self.data["tn_id"] + ".md"
            path_report_trial_network = os.path.join(REPORT_DIRECTORY, report_trial_network_name)
            with open(path_report_trial_network, "a") as result_msg_file:
                result_msg_file.write(result_msg)
            log_handler.info("Saved entity deployment information")
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 500)