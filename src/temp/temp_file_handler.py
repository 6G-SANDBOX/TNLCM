import os

from tempfile import NamedTemporaryFile
from yaml import dump

TEMP_FILES_PATH = os.path.join(os.getcwd(), "src", "temp", "files")

class TempFileHandler:

    def __init__(self):
        """Constructor"""
        os.makedirs(TEMP_FILES_PATH, exist_ok=True)
    
    def create_component_temp_file(self, component_name, entity_public, tn_vxlan_id=None):
        """Create temporary files for each component that is deployed in the pipeline and returns the path to the file"""
        with NamedTemporaryFile(delete=False, dir=TEMP_FILES_PATH, suffix=".yaml", mode='w') as component_temp_file:
            entity_public["tnlcm_callback"] = os.getenv("CALLBACK_URL")
            if tn_vxlan_id is not None:
                entity_public["one_component_networks"] = [0, int(tn_vxlan_id)]
                if component_name == "tn_bastion":
                    entity_public["one_bastion_wireguard_allowed_networks"] = "192.168.199.0/24"
            dump(entity_public, component_temp_file, default_flow_style=False)
        return component_temp_file.name