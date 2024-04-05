import os

from tempfile import NamedTemporaryFile
from json import load
from yaml import dump

TEMP_FILES_PATH = os.path.join(os.getcwd(), "src", "temp", "files")

class TempFileHandler:

    def __init__(self):
        """Constructor"""
        os.makedirs(TEMP_FILES_PATH, exist_ok=True)
    
    def extract_tn_vxlan_ids(self, entity_data, descriptor_trial_network, report_directory, tn_id):
        """Extract vxlan ids for the dependencies"""
        tn_vxlan_ids = []
        entity_depends_on = entity_data["depends_on"]
        if entity_depends_on:
            for entity_dependency in entity_depends_on:
                for descriptor_entities_name, descriptor_entities_data in descriptor_trial_network.items():
                    if descriptor_entities_name == entity_dependency and descriptor_entities_data["type"] == "tn_vxlan":
                        descriptor_entity_report_file = os.path.join(report_directory, descriptor_entities_name + "_" + tn_id + ".json")
                        if os.path.isfile(descriptor_entity_report_file):
                            with open(descriptor_entity_report_file, "r") as file:
                                json_data = load(file)
                                tn_vxlan_id = json_data["tn_vxlan_id"]
                                tn_vxlan_ids.append(int(tn_vxlan_id))
        return tn_vxlan_ids

    def create_entity_temp_file(self, entity_data, descriptor_trial_network, report_directory, tn_id):
        """Create temporary files for each entity that is deployed in the pipeline and returns the path to the file"""
        entity_public = entity_data["public"]
        entity_type = entity_data["type"]
        with NamedTemporaryFile(delete=False, dir=TEMP_FILES_PATH, suffix=".yaml", mode='w') as entity_temp_file:
            entity_public["tnlcm_callback"] = os.getenv("CALLBACK_URL")
            if entity_type != "tn_vxlan":
                entity_public["one_component_networks"] = [0] + self.extract_tn_vxlan_ids(entity_data, descriptor_trial_network, report_directory, tn_id)
                if entity_type == "tn_bastion":
                    entity_public["one_bastion_wireguard_allowed_networks"] = "192.168.199.0/24"
            dump(entity_public, entity_temp_file, default_flow_style=False)
        return entity_temp_file.name