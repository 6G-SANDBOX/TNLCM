import os

from json import dump, load
from base64 import b64decode

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import KeyNotFoundError, CustomUnicodeDecodeError

REPORT_DIRECTORY = os.path.join(os.getcwd(), "src", "callback", "reports")
JENKINS_RESULT_KEYS = ["tn_id", "library_component_name", "entity_name", "success", "markdown", "output"]

class CallbackHandler:

    def __init__(self, data=None, trial_network_handler=None, sixgsandbox_sites_handler=None):
        """Constructor"""
        self.data = data
        self.trial_network_handler = trial_network_handler
        self.sixgsandbox_sites_handler = sixgsandbox_sites_handler
        os.makedirs(REPORT_DIRECTORY, exist_ok=True)

    def save_decoded_results(self):
        """Save decoded deployment information of each component received by Jenkins"""
        # TODO: Check if success is true to continue with the pipeline
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
                else:
                    decoded_data[key_data] = b64decode(value_data).decode("utf-8")

            entity_file_name = decoded_data["tn_id"] + "-" + decoded_data["library_component_name"] + "-" + decoded_data["entity_name"] + ".json"
            path_entity_file_name = os.path.join(REPORT_DIRECTORY, entity_file_name)

            with open(path_entity_file_name, "w") as entity_file:
                dump(decoded_data, entity_file)

            entity_name = decoded_data["entity_name"]
            log_handler.info(f"Information of the '{entity_name}' entity save in the file '{entity_file_name}' located in the path '{path_entity_file_name}'")

            report_trial_network_name = decoded_data["tn_id"] + ".md"
            path_report_trial_network = os.path.join(REPORT_DIRECTORY, report_trial_network_name)

            with open(path_report_trial_network, "a") as report_trial_network:
                report_trial_network.write(decoded_data["markdown"])

            log_handler.info(f"'markdown' of the '{entity_name}' entity save in the report file '{report_trial_network_name}' located in the path '{path_report_trial_network}'")
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 401)

    def add_entity_input(self, entity_name, entity_data, jenkins_deployment_site):
        """Add parameters to the entity file"""
        log_handler.info(f"Add parameters to entity '{entity_name}'")
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

    def _get_vxlan_ids(self, vxlan_names):
        """Extract vxlan ids"""
        vnets_id = []
        if isinstance(vxlan_names, list):
            for vxlan in vxlan_names:
                vnets_id.extend(self._vxlan_ids(vxlan))
        else:
            vnets_id = self._vxlan_ids(vxlan_names)[0]
        return vnets_id

    def _vxlan_ids(self, vxlan_name):
        """Return list with vxlan ids"""
        log_handler.info(f"Get id of the '{vxlan_name}' vxlan")
        vxlan_ids = []
        tn_descriptor = self.trial_network_handler.get_trial_network_descriptor()["trial_network"]
        tn_id = self.trial_network_handler.tn_id
        if vxlan_name in tn_descriptor.keys():
            entity_data = tn_descriptor[vxlan_name]
            entity_type = entity_data["type"]
            if entity_type == "tn_vxlan" or entity_type == "vxlan":
                entity_report_file = os.path.join(REPORT_DIRECTORY, f"{tn_id}-{entity_type}-{vxlan_name}.json")
                if os.path.isfile(entity_report_file):
                    with open(entity_report_file, "r") as file:
                        json_data = load(file)
                        tn_vxlan_id = json_data["tn_vxlan_id"]
                        vxlan_ids.append(int(tn_vxlan_id))
        return vxlan_ids
    
    def get_path_report_trial_network(self):
        """Return path where report of trial network is stored"""
        return os.path.join(REPORT_DIRECTORY, self.trial_network_handler.tn_id)