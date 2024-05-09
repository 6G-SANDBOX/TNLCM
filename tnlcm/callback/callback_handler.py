import os

from json import dump, load
from base64 import b64decode

from tnlcm.logs.log_handler import log_handler
from tnlcm.exceptions.exceptions_handler import KeyNotFoundError, CustomUnicodeDecodeError, CustomFileNotFoundError

REPORT_DIRECTORY = os.path.join(os.getcwd(), "tnlcm", "callback", "reports")
JENKINS_RESULT_KEYS = ["tn_id", "library_component_name", "entity_name", "success", "output", "markdown"]

class CallbackHandler:

    def __init__(self, data=None, trial_network=None, sixglibrary_handler=None, sixgsandbox_sites_handler=None):
        """Constructor"""
        self.data = data
        self.sixglibrary_handler = sixglibrary_handler
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
                else:
                    decoded_data[key_data] = b64decode(value_data).decode("utf-8")
            
            entity_name = decoded_data["entity_name"]
            library_component_name = decoded_data["library_component_name"]
            tn_id = decoded_data["tn_id"]
            success = decoded_data["success"]
            output_jenkins = decoded_data["output"]
            markdown = decoded_data["markdown"]
            
            components = self.sixglibrary_handler.extract_components_6glibrary()
            output_parts_components = self.sixglibrary_handler.extract_output_part_component_6glibrary(components)
            self._is_output_correct(output_jenkins, output_parts_components[library_component_name])

            entity_file_name = tn_id + "-" + library_component_name + "-" + entity_name + ".json"
            path_entity_file_name = os.path.join(REPORT_DIRECTORY, entity_file_name)
            
            with open(path_entity_file_name, "w") as entity_file:
                dump(decoded_data, entity_file)
            
            log_handler.info(f"Information of the '{entity_name}' entity save in the file '{entity_file_name}' located in the path '{path_entity_file_name}'")

            report_trial_network_name = tn_id + ".md"
            path_report_trial_network = os.path.join(REPORT_DIRECTORY, report_trial_network_name)

            with open(path_report_trial_network, "a") as report_trial_network:
                report_trial_network.write(markdown)

            log_handler.info(f"'Markdown' of the '{entity_name}' entity save in the report file '{report_trial_network_name}' located in the path '{path_report_trial_network}'")
        except UnicodeDecodeError:
            raise CustomUnicodeDecodeError("Unicode decoding error", 401)

    def _is_output_correct(self, output_jenkins, output_component):
        """Check if output received by Jenkins is the same as the output of the 6G-Library"""
        log_handler.info("Check if output received by Jenkins is the same as the output of the 6G-Library")
        if output_jenkins and output_component:
            list1 = output_jenkins.keys()
            list2 = output_component.keys()
            if len(list1) != len(list2):
                return False
            for key in list1:
                if key not in list2:
                    return False
            return True
        else:
            return False

    def add_entity_input_parameters(self, entity_name, entity_data, jenkins_deployment_site):
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
        entity_type, output, value_output = vxlan_path.split(".")
        tn_id = self.trial_network.tn_id
        if "-" in entity_type:
            entity_type, entity_name = entity_type.split("-")
        file_path = os.path.join(REPORT_DIRECTORY, f"{tn_id}-{entity_type}-{entity_name}.json") if entity_name else os.path.join(REPORT_DIRECTORY, f"{tn_id}-{entity_type}.json")
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
    
    def exists_path_entity_trial_network(self, entity_name, entity_type):
        """Return true if exists entity file with information received by Jenkins"""
        path_entity_trial_network = os.path.join(REPORT_DIRECTORY, f"{self.trial_network.tn_id}-{entity_type}-{entity_name}.json")
        return os.path.exists(path_entity_trial_network)