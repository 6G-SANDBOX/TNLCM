import os

from json import dump, load
from yaml import safe_load, YAMLError
from base64 import b64decode

from tnlcm.logs.log_handler import log_handler
from tnlcm.exceptions.exceptions_handler import KeyNotFoundError, CustomUnicodeDecodeError, InvalidContentFileError, CustomFileNotFoundError, KeyNotFoundError

REPORT_DIRECTORY = os.path.join(os.getcwd(), "tnlcm", "callback", "reports")
SIXGLIBRARY_DIRECTORY = os.path.join(os.getcwd(), "tnlcm", "sixglibrary")
JENKINS_RESULT_KEYS = ["tn_id", "component_type", "custom_name", "success", "output", "markdown"]

class CallbackHandler:

    def __init__(self, data=None, trial_network=None, sixgsandbox_sites_handler=None):
        """Constructor"""
        self.data = data
        self.trial_network = trial_network
        self.sixgsandbox_sites_handler = sixgsandbox_sites_handler
        os.makedirs(REPORT_DIRECTORY, exist_ok=True)

    def save_decoded_results(self):
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
        public_file = os.path.join(SIXGLIBRARY_DIRECTORY, os.getenv("GIT_6GLIBRARY_REPOSITORY_NAME"), component_type, ".tnlcm", "public.yaml")
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

    def add_entity_input_parameters(self, entity, entity_data, jenkins_deployment_site):
        """Add parameters to the entity file"""
        log_handler.info(f"Add parameters to entity '{entity}'")
        entity_input = entity_data["input"]
        entity_type = entity_data["type"]
        if entity_type == "tn_bastion":
            self.sixgsandbox_sites_handler.git_clone_6gsandbox_sites()
            entity_input["one_component_networks"] = [self.sixgsandbox_sites_handler.extract_site_public_network_id(jenkins_deployment_site)] + self._get_vxlan_ids(entity_input["one_component_networks"])
            entity_input["one_bastion_wireguard_allowed_networks"] = "192.168.199.0/24"
        elif entity_type == "vm_kvm_very_small" or entity_type == "vm_kvm_small" or entity_type == "vm_kvm_medium" or entity_type == "vm_kvm_large" or entity_type == "vm_kvm_extra_large":
            self.sixgsandbox_sites_handler.git_clone_6gsandbox_sites()
            entity_input["one_component_networks"] = [self.sixgsandbox_sites_handler.extract_site_default_network_id(jenkins_deployment_site)] + self._get_vxlan_ids(entity_input["one_component_networks"])
        elif entity_type == "k8s_medium":
            entity_input["external_vnet_id"] = self._get_vxlan_ids(entity_input["external_vnet_id"])
            entity_input["internal_vnet_id"] = self._get_vxlan_ids(entity_input["internal_vnet_id"])
        elif entity_type == "ueransim":
            entity_input["one_component_networks"] = self._get_vxlan_ids(entity_input["one_component_networks"])
        return entity_input

    def _get_vxlan_ids(self, vxlan_paths):
        """Extract vxlan ids"""
        vnets_id = []
        if isinstance(vxlan_paths, list):
            for vxlan_path in vxlan_paths:
                vnets_id.append(self._extract_vxlan_id(vxlan_path))
        else:
            vnets_id.append(self._extract_vxlan_id(vxlan_paths))
        return vnets_id

    def _extract_vxlan_id(self, vxlan_path):
        """Return vxlan id"""
        log_handler.info(f"Get identifier of '{vxlan_path}' vxlan")
        entity_name, output, value_output = vxlan_path.split(".")
        tn_id = self.trial_network.tn_id
        file_path = os.path.join(REPORT_DIRECTORY, f"{tn_id}-{entity_name}.json")
        with open(file_path, "r") as file:
            data = load(file)
        return data[output][value_output]
    
    def get_path_report_trial_network(self):
        """Return path where report of trial network is stored"""
        path_report_trial_network = os.path.join(REPORT_DIRECTORY, f"{self.trial_network.tn_id}.md")
        if os.path.exists(path_report_trial_network):
            return path_report_trial_network
        else:
            raise CustomFileNotFoundError("Trial network report file has not been found", 404)
    
    def exists_path_entity_trial_network(self, entity, entity_type):
        """Return true if exists entity file with information received by Jenkins"""
        log_handler.info(f"Check whether the file of the '{entity}' entity has been created.")
        path_entity_trial_network = os.path.join(REPORT_DIRECTORY, f"{self.trial_network.tn_id}-{entity}.json")
        return os.path.exists(path_entity_trial_network)