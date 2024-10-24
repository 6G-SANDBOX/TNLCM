import os

from mongoengine import Document, StringField, DictField

from conf import SixGLibrarySettings, TnlcmSettings
from core.utils.file_handler import load_yaml, save_json, save_file
from core.utils.parser_handler import decode_base64
from core.exceptions.exceptions_handler import CustomCallbackException

class CallbackModel(Document):

    tn_id = StringField(required=True)
    entity_name = StringField(required=True)
    component_type = StringField(required=True)
    custom_name = StringField(required=True)
    success = StringField(default=False)
    markdown = StringField(required=True)
    output = DictField(required=True)

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "callback"
    }

    def decode_data(self, data: dict) -> dict:
        """
        Decode response received by Jenkins

        :param data: dictionary with encode values, ``dict``
        :return: dictionary with decode values, ``dict``
        :raises CustomCallbackException:
        """
        decoded_data = {}
        for key_data, value_data in data.items():
            if key_data not in self._fields_ordered[1:]:
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
        
        self.tn_id = decoded_data["tn_id"]
        self.custom_name = decoded_data["custom_name"]
        self.component_type = decoded_data["component_type"]
        self.success = decoded_data["success"]
        self.output = decoded_data["output"]
        self.markdown = decoded_data["markdown"]
        self.decoded_data = decoded_data
        self.entity_name = f"{self.component_type}-{self.custom_name}" if self.custom_name != "None" else self.component_type

        return decoded_data

    def save_data_file(self, data: dict) -> None:
        """
        Save data in files

        :param data: dictionary with decode values, ``dict``
        """
        save_json(data=data, file_path=os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, self.tn_id, f"{self.entity_name}.json"))
        save_file(data=self.markdown, file_path=os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, self.tn_id, f"{self.tn_id}.md"), mode="a", encoding="utf-8")

    def matches_expected_output(self) -> bool:
        """
        Function to check that the output keys received by Jenkins are the same as the output keys defined in 6G-Library

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

    def to_dict(self) -> dict:
        return {
            "tn_id": self.tn_id,
            "entity_name": self.entity_name,
            "component_type": self.component_type,
            "custom_name": self.custom_name,
            "success": self.success,
            "markdown": self.markdown,
            "output": self.output
        }
    
    def __repr__(self) -> str:
        return "<Callback #%s>" % (self.tn_id)