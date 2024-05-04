from werkzeug.utils import secure_filename
from json import dumps
from yaml import safe_load, YAMLError

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import InvalidFileExtensionError, InvalidContentError, TrialNetworkDescriptorEmptyError, TrialNetworkEntityNotInDescriptorError

class TrialNetworkDescriptorHandler:

    def __init__(self, current_user=None, descriptor=None):
        """Constructor"""
        self.current_user = current_user
        self.descriptor = descriptor
    
    def check_descriptor(self):
        """Check that the descriptor file is well constructed and that its extension is yaml or yml"""
        try:
            log_handler.info("Check if descriptor extension is yml or yaml file")
            filename = secure_filename(self.descriptor.filename)
            if '.' in filename and filename.split('.')[-1].lower() in ["yml", "yaml"]:
                self.descriptor = safe_load(self.descriptor.stream)
            else:
                raise InvalidFileExtensionError("Invalid descriptor format. Only 'yml' or 'yaml' files will be further processed", 422)
            if self.descriptor["trial_network"] is None:
                raise TrialNetworkDescriptorEmptyError("Trial network descriptor empty", 400)
        except YAMLError:
            raise InvalidContentError("Descriptor content not properly parsed", 422)

    def add_entity_mandatory_tn_vxlan(self):
        """Add the entity vxlan to the descriptor (mandatory)"""
        log_handler.info("Add mandatory tn_vxlan to descriptor")
        if not self._is_entity_descriptor("mandatory_tn_vxlan"):
            entity_data = {
                "input": {
                    "one_vxlan_name": "mandatory_tn_vxlan"
                }
            }
            self._add_entity_descriptor("mandatory_tn_vxlan", entity_data)

    def add_entity_mandatory_tn_bastion(self):
        """Add the entity bastion to the descriptor (mandatory)"""
        log_handler.info("Add mandatory tn_bastion to descriptor")
        if not self._is_entity_descriptor("mandatory_tn_bastion"):
            entity_data = {
                "needs": ["mandatory_tn_vxlan"],
                "input": None
            }
            self._add_entity_descriptor("mandatory_tn_bastion", entity_data)
    
    def _is_entity_descriptor(self, entity):
        """Return true if an entity is in descriptor"""
        is_entity = False
        for entity_name, entity_data in self.descriptor["trial_network"].items():
            if entity_name == entity and entity_data is not None:
                is_entity = True
                break
        return is_entity

    def _add_entity_descriptor(self, entity_name, entity_data):
        """Return a new descriptor containing the newly added entity"""
        self.descriptor["trial_network"][entity_name] = entity_data

    def sort_descriptor(self):
        """Recursive method that returns the raw descriptor and a new descriptor sorted according to dependencies (needs)"""
        log_handler.info("Start order of the entities of the descriptor")
        entities = self.descriptor["trial_network"]
        ordered_entities = {}

        def dfs(entity):
            if entity not in entities.keys():
                raise TrialNetworkEntityNotInDescriptorError("Name of the dependency does not match the name of some entity defined in the descriptor", 404)
            if entity in ordered_entities:
                return
            if "needs" in entities[entity]:
                for dependency in entities[entity]["needs"]:
                    dfs(dependency)
            ordered_entities[entity] = entities[entity]

        for entity in entities:
            dfs(entity)
        
        log_handler.info("End order of the entities of the descriptor")
        return dumps(self.descriptor), dumps({"trial_network": ordered_entities})