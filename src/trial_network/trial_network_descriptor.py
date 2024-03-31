from werkzeug.utils import secure_filename
from json import dumps
from yaml import safe_load, YAMLError

from src.exceptions.exceptions_handler import TrialNetworkDescriptorInvalidExtensionError, TrialNetworkDescriptorEmptyError, TrialNetworkDescriptorInvalidContentError

class TrialNetworkDescriptorHandler:

    def __init__(self, current_user, descriptor):
        """Constructor"""
        self.current_user = current_user
        self.descriptor = descriptor
    
    def check_descriptor(self):
        """Check that the descriptor file is well constructed and that its extension is yaml or yml"""
        try:
            filename = secure_filename(self.descriptor.filename)
            if '.' in filename and filename.split('.')[-1].lower() in ['yml', 'yaml']:
                self.descriptor = safe_load(self.descriptor.stream)
            else:
                raise TrialNetworkDescriptorInvalidExtensionError("Invalid descriptor format. Only 'yml' or 'yaml' files will be further processed", 422)
            if self.descriptor["trial_network"] is None:
                raise TrialNetworkDescriptorEmptyError("Trial network descriptor empty", 400)
        except YAMLError:
            raise TrialNetworkDescriptorInvalidContentError("The descriptor content is not parsed correctly", 422)

    def add_component_tn_vxlan(self):
        """Add the component tn_vxlan to the descriptor (mandatory)"""
        # TODO: fix if update descriptor
        if not self.is_component_descriptor("tn_vxlan"):
            component_data = {
                "public": {
                    "one_vxlan_name": "tn_vxlan"
                }
            }
            self.add_component_descriptor("tn_vxlan", component_data)

    def add_component_tn_bastion(self):
        """Add the component tn_bastion to the descriptor (mandatory)"""
        # TODO: fix if update descriptor
        if not self.is_component_descriptor("tn_bastion"):
            component_data = {
                "depends_on": ["tn_vxlan"],
                "public": None
            }
            self.add_component_descriptor("tn_bastion", component_data)
    
    def is_component_descriptor(self, component):
        """Return true if a component is in descriptor"""
        # TODO: fix if update descriptor
        is_component = False
        for component_name, component_data in self.descriptor["trial_network"].items():
            if component_name == component and component_data is not None:
                is_component = True
                break
        return is_component

    def add_component_descriptor(self, component_name, component_data):
        """Return a new descriptor containing the newly added component"""
        # TODO: fix if update descriptor
        self.descriptor["trial_network"][component_name] = component_data

    def sort_descriptor(self):
        """Recursive function that returns the raw descriptor and a new descriptor sorted according to dependencies"""
        components = self.descriptor["trial_network"]
        ordered_components = {}

        def dfs(component):
            if component in ordered_components:
                return
            if "depends_on" in components[component]:
                for dependency in components[component]["depends_on"]:
                    dfs(dependency)
            ordered_components[component] = components[component]

        for component in components:
            dfs(component)

        return dumps(self.descriptor), dumps({"trial_network": ordered_components})