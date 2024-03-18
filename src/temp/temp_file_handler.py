import os

from tempfile import NamedTemporaryFile
from yaml import dump

TEMP_FILES_PATH = os.path.join(os.getcwd(), "src", "temp", "files")

class TempFileHandler:

    def __init__(self):
        os.makedirs(TEMP_FILES_PATH, exist_ok=True)
    
    def create_component_temp_file(self, component_name, component_public, tn_vxlan_id=None):
        with NamedTemporaryFile(delete=False, dir=TEMP_FILES_PATH, suffix=".yaml", mode='w') as component_temp_file:
            if component_public is None:
                component_public = {}
            component_public["tnlcm_callback"] = os.getenv("CALLBACK_URL")
            if tn_vxlan_id is not None:
                component_public["one_component_networks"] = [0, int(tn_vxlan_id)]
                if component_name == "tn_bastion":
                    component_public["one_bastion_wireguard_allowed_networks"] = "192.168.199.0/24"
            dump(component_public, component_temp_file, default_flow_style=False)
        return component_temp_file.name