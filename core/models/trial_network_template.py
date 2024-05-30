from werkzeug.utils import secure_filename
from json import dumps, loads
from yaml import safe_load, YAMLError
from string import ascii_lowercase, digits
from random import choice
from datetime import datetime, timezone
from mongoengine import Document, StringField, DateTimeField

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import InvalidFileExtensionError, InvalidContentFileError, TrialNetworkEntityNotInDescriptorError

class TrialNetworkTemplateModel(Document):
    user_created = StringField(max_length=100)
    tn_id = StringField(max_length=10, unique=True)
    tn_date_created_utc = DateTimeField(default=datetime.now(timezone.utc))
    tn_raw_descriptor = StringField()
    tn_sorted_descriptor = StringField()

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "trial_networks_templates"
    }

    def set_tn_id(self, size=6, chars=ascii_lowercase+digits, tn_id=None):
        """Generate random tn_id using [a-z][0-9]"""
        if not tn_id:
            self.tn_id = choice(ascii_lowercase) + ''.join(choice(chars) for _ in range(size))
        else:
            self.tn_id = tn_id

    def set_tn_raw_descriptor(self, tn_descriptor_file):
        """Check the descriptor file is well constructed and its extension is yaml or yml"""
        try:
            filename = secure_filename(tn_descriptor_file.filename)
            if '.' in filename and filename.split('.')[-1].lower() in ["yml", "yaml"]:
                tn_raw_descriptor = safe_load(tn_descriptor_file.stream)
            else:
                raise InvalidFileExtensionError("Invalid descriptor format. Only 'yml' or 'yaml' files will be further processed", 422)
            if len(tn_raw_descriptor.keys()) > 1 or not "trial_network" in tn_raw_descriptor.keys():
                raise InvalidContentFileError("Trial network descriptor is not parsed correctly", 422)
            self.tn_raw_descriptor = self.descriptor_to_json(tn_raw_descriptor)
        except YAMLError:
            raise InvalidContentFileError("Trial network descriptor is not parsed correctly", 422)

    def set_tn_sorted_descriptor(self):
        """Recursive method that return the raw descriptor and a new descriptor sorted according to dependencies"""
        log_handler.info("Start order of the entities of the descriptor")
        entities = self.json_to_descriptor(self.tn_raw_descriptor)["trial_network"]
        ordered_entities = {}

        def dfs(entity):
            if entity not in entities.keys():
                raise TrialNetworkEntityNotInDescriptorError("Name of the dependency does not match the name of some entity defined in the descriptor", 404)
            if entity in ordered_entities:
                return
            if "dependencies" in entities[entity]:
                for dependency in entities[entity]["dependencies"]:
                    dfs(dependency)
            ordered_entities[entity] = entities[entity]

        for entity in entities:
            dfs(entity)
        
        log_handler.info("End order of the entities of the descriptor")
        self.tn_sorted_descriptor = self.descriptor_to_json({"trial_network": ordered_entities})

    def descriptor_to_json(self, descriptor):
        """Convert descriptor to json"""
        return dumps(descriptor)

    def json_to_descriptor(self, descriptor):
        """Convert descriptor in json to Python object"""
        return loads(descriptor)

    def to_dict(self):
        return {
            "user_created": self.user_created,
            "tn_id": self.tn_id
        }
    
    def to_dict_full(self):
        return {
            "user_created": self.user_created,
            "tn_id": self.tn_id,
            "tn_date_created_utc": self.tn_date_created_utc.isoformat(),
            "tn_raw_descriptor": self.json_to_descriptor(self.tn_raw_descriptor),
            "tn_sorted_descriptor": self.json_to_descriptor(self.tn_sorted_descriptor)
        }

    def __repr__(self):
        return "<TrialNetwork #%s>" % (self.tn_id)