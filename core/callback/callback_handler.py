import os

from conf.tnlcm import TnlcmSettings
from conf.sixg_library import SixGLibrarySettings
from core.utils.file_handler import load_yaml, save_json, save_file
from core.utils.parser_handler import decode_base64
from core.exceptions.exceptions_handler import CustomCallbackException

KEY_JENKINS = {"tn_id", "custom_name", "component_type", "success", "output", "markdown"}

class CallbackHandler:

    def __init__(self, encoded_data: dict) -> None:
        """
        Constructor
        
        :param encoded_data: dictionary with encode values received by Jenkins, ``dict``
        """
        self.encoded_data = encoded_data
        self.decoded_data = self.decode_data()
        self.tn_id = self.decoded_data["tn_id"]
        self.custom_name = self.decoded_data["custom_name"]
        self.component_type = self.decoded_data["component_type"]
        self.success = self.decoded_data["success"]
        self.output = self.decoded_data["output"]
        self.markdown = self.decoded_data["markdown"]
        self.entity_name = f"{self.component_type}-{self.custom_name}" if self.custom_name != "None" else self.component_type
    
    def decode_data(self) -> dict:
        """
        Decode response received by Jenkins
        
        :return: dictionary with decode values, ``dict``
        :raises CustomCallbackException:
        """
        decoded_data = {}
        for key_data, value_data in self.encoded_data.items():
            if key_data not in KEY_JENKINS:
                raise CustomCallbackException("Invalid key received by Jenkins", 500)
            if key_data == "output":
                decoded_output = {}
                for key_output, value_output in value_data.items():
                    decoded_output[key_output] = decode_base64(encoded_data=value_output)
                decoded_data[key_data] = decoded_output
            elif key_data == "success":
                decoded_data[key_data] = value_data
            else:
                decoded_data[key_data] = decode_base64(encoded_data=value_data)
        return decoded_data
    
    def matches_expected_output(self) -> bool:
        """
        Function to verify that the output keys received by Jenkins are the same as the output keys defined in 6G-Library

        :return: True if output received by Jenkins is the same as the output defined in 6G-Library. Otherwise False, ``bool``
        :raises CustomCallbackException:
        """
        public_file = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, self.tn_id, SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME, self.component_type, ".tnlcm", "public.yaml")
        if not os.path.exists(public_file):
            raise CustomCallbackException(f"File '{public_file}' not found", 404)
        public_data = load_yaml(file_path=public_file, mode="rt", encoding="utf-8")
        if "output" not in public_data:
            raise CustomCallbackException(f"Key 'output' is missing in the file located in the path '{public_file}'", 404)
        output_library = public_data["output"]
        if output_library and len(self.component_type) > 0 and self.output and len(self.output) > 0:
            return set(self.output.keys()) == set(output_library.keys())
        if not output_library and len(self.output) == 0:
            return True
        return False
    
    def save_data_file(self) -> None:
        """
        Save data in files
        """
        directory_path = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, self.tn_id)
        os.makedirs(os.path.join(directory_path, "output"), exist_ok=True)
        save_json(data=self.decoded_data, file_path=os.path.join(directory_path, "output", f"{self.entity_name}.json"))
        save_file(data=self.markdown, file_path=os.path.join(directory_path, f"{self.tn_id}.md"), mode="a", encoding="utf-8")