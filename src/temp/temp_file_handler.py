import os

from json import load
from yaml import dump
from tempfile import NamedTemporaryFile

from src.logs.log_handler import log_handler

TEMP_FILES_PATH = os.path.join(os.getcwd(), "src", "temp", "files")

class TempFileHandler:

    def __init__(self):
        """Constructor"""
        os.makedirs(TEMP_FILES_PATH, exist_ok=True)

    def find_vxlan_ids(self, vxlan_names, tn_descriptor, report_directory, tn_id):
        """Extract vxlan ids"""
        vnets_id = []
        if isinstance(vxlan_names, list):
            for vxlan in vxlan_names:
                vnets_id.extend(self._get_vxlan_ids(vxlan, tn_descriptor, report_directory, tn_id))
        else:
            vnets_id = self._get_vxlan_ids(vxlan_names, tn_descriptor, report_directory, tn_id)[0]
        return vnets_id

    def _get_vxlan_ids(self, vxlan_name, tn_descriptor, report_directory, tn_id):
        vxlan_ids = []
        for descriptor_entities_name, descriptor_entities_data in tn_descriptor.items():
            if descriptor_entities_name == vxlan_name and (descriptor_entities_data["type"] == "tn_vxlan" or descriptor_entities_data["type"] == "vxlan"):
                descriptor_entity_report_file = os.path.join(report_directory, f"{descriptor_entities_name}_{tn_id}.json")
                if os.path.isfile(descriptor_entity_report_file):
                    with open(descriptor_entity_report_file, "r") as file:
                        json_data = load(file)
                        tn_vxlan_id = json_data["tn_vxlan_id"]
                        vxlan_ids.append(int(tn_vxlan_id))
        return vxlan_ids

    def _add_private_entity_parameters(self, entity_name, entity_data, tn_descriptor, report_directory, tn_id):
        """Add private parameters to the entity file"""
        log_handler.info(f"Adding private part to entity '{entity_name}'")
        entity_public = entity_data["public"]
        entity_type = entity_data["type"]
        entity_public["tnlcm_callback"] = os.getenv("CALLBACK_URL")
        if entity_type == "tn_bastion":
            entity_public["one_component_networks"] = [280] + self.find_vxlan_ids(entity_public["one_component_networks"], tn_descriptor, report_directory, tn_id)
            entity_public["one_bastion_wireguard_allowed_networks"] = "192.168.199.0/24"
        elif entity_type == "vm_kvm_very_small" or entity_type == "vm_kvm_small" or entity_type == "vm_kvm_medium" or entity_type == "vm_kvm_large" or entity_type == "vm_kvm_extra_large":
            entity_public["one_component_networks"] = [0] + self.find_vxlan_ids(entity_public["one_component_networks"], tn_descriptor, report_directory, tn_id)
        elif entity_type == "k8s_medium":
            entity_public["external_vnet_id"] = self.find_vxlan_ids(entity_public["external_vnet_id"], tn_descriptor, report_directory, tn_id)
            entity_public["internal_vnet_id"] = self.find_vxlan_ids(entity_public["internal_vnet_id"], tn_descriptor, report_directory, tn_id)
        elif entity_type == "ueransim":
            entity_public["one_component_networks"] = self.find_vxlan_ids(entity_public["one_component_networks"], tn_descriptor, report_directory, tn_id)
        return entity_public

    def create_entity_temp_file(self, entity_name, entity_data, tn_descriptor, report_directory, tn_id):
        """Create temporary files for each entity that is deployed in the pipeline and returns the path to the file"""
        log_handler.info(f"Creating a temporary file with the private and public part for the '{entity_name}' entity. It is required to send it to the pipeline")
        with NamedTemporaryFile(delete=False, dir=TEMP_FILES_PATH, suffix=".yaml", mode='w') as entity_temp_file:
            entity_public = self._add_private_entity_parameters(entity_name, entity_data, tn_descriptor, report_directory, tn_id)
            dump(entity_public, entity_temp_file, default_flow_style=False)
        return entity_temp_file.name