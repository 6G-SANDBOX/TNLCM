from werkzeug.utils import secure_filename
from json import dumps, loads
from yaml import safe_load, YAMLError
from string import ascii_lowercase, digits
from random import choice
from datetime import datetime, timezone

from tnlcm.logs.log_handler import log_handler
from mongoengine import Document, StringField, DateTimeField
from tnlcm.exceptions.exceptions_handler import InvalidFileExtensionError, InvalidContentFileError, TrialNetworkEntityNotInDescriptorError

class TrialNetworkModel(Document):
    user_created = StringField(max_length=255, required=True)
    tn_id = StringField(max_length=255, required=True, unique=True)
    tn_date_created_utc = DateTimeField(required=True, default=datetime.now(timezone.utc))
    tn_raw_descriptor = StringField(required=True)
    tn_sorted_descriptor = StringField(required=True)
    tn_report = StringField(required=False)

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "trial_networks"
    }

    def __init__(self, user_created, tn_id=None, tn_raw_descriptor=None, tn_sorted_descriptor=None, tn_report=None, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)
        self.user_created = user_created
        self.tn_id = tn_id
        self.tn_raw_descriptor = tn_raw_descriptor
        self.tn_sorted_descriptor = tn_sorted_descriptor
        self.tn_report = tn_report

    def set_tn_id(self, size=6, chars=ascii_lowercase + digits):
        """Generate random tn_id using [a-z][0-9]"""
        self.tn_id = choice(ascii_lowercase) + ''.join(choice(chars) for _ in range(size))

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
        """Recursive method that returns the raw descriptor and a new descriptor sorted according to dependencies (needs)"""
        log_handler.info("Start order of the entities of the descriptor")
        entities = self.json_to_descriptor(self.tn_raw_descriptor)["trial_network"]
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
        self.tn_sorted_descriptor = self.descriptor_to_json({"trial_network": ordered_entities})

    def set_tn_report(self, report_file):
        with open(report_file, "r") as file:
            markdown_content = file.read()
        self.tn_report = markdown_content

    def descriptor_to_json(self, descriptor):
        return dumps(descriptor)

    def json_to_descriptor(self, descriptor):
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