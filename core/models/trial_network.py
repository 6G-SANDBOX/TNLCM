import re

from werkzeug.utils import secure_filename
from json import dumps, loads
from yaml import safe_load, YAMLError
from string import ascii_lowercase, digits
from random import choice
from datetime import datetime, timezone
from mongoengine import Document, StringField, DateTimeField

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import InvalidFileExtensionError, InvalidContentFileError, TrialNetworkInvalidStatusError, TrialNetworkInvalidDescriptorError

TN_STATE_MACHINE = ["validated", "suspended", "activated", "failed", "destroyed"]
COMPONENTS_EXCLUDE_CUSTOM_NAME = ["tn_vxlan", "tn_bastion", "tn_init", "tsn"]
REQUIRED_FIELDS_DESCRIPTOR = ["type", "dependencies", "input"]

class TrialNetworkModel(Document):
    user_created = StringField(max_length=100)
    tn_id = StringField(max_length=10, unique=True)
    tn_state = StringField(max_length=50)
    tn_date_created_utc = DateTimeField(default=datetime.now(timezone.utc))
    tn_raw_descriptor = StringField()
    tn_sorted_descriptor = StringField()
    tn_deployed_descriptor = StringField()
    tn_report = StringField()
    deployment_job_name = StringField()
    destroy_job_name = StringField()
    deployment_site = StringField()
    github_6g_library_commit_id = StringField()
    github_6g_sandbox_sites_commit_id = StringField()

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "trial_networks"
    }

    def set_tn_id(self, size=6, chars=ascii_lowercase+digits, tn_id=None):
        """Generate random tn_id using [a-z][0-9]"""
        if not tn_id:
            self.tn_id = choice(ascii_lowercase) + ''.join(choice(chars) for _ in range(size))
        else:
            self.tn_id = tn_id

    def set_tn_state(self, tn_state):
        """Set state of trial network"""
        if tn_state not in TN_STATE_MACHINE:
            raise TrialNetworkInvalidStatusError(f"Trial network '{tn_state}' state not found", 404)
        self.tn_state = tn_state

    def set_tn_raw_descriptor(self, tn_descriptor_file):
        """Check the descriptor file is well constructed and its extension is yaml or yml"""
        try:
            filename = secure_filename(tn_descriptor_file.filename)
            if '.' in filename and filename.split('.')[-1].lower() in ["yml", "yaml"]:
                tn_raw_descriptor = safe_load(tn_descriptor_file.stream)
            else:
                raise InvalidFileExtensionError("Invalid descriptor format. Only 'yml' or 'yaml' files will be further processed", 422)
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
                raise TrialNetworkInvalidDescriptorError("Name of the dependency does not match the name of some entity defined in the descriptor", 404)
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
        self.tn_deployed_descriptor = self.descriptor_to_json({"trial_network": ordered_entities})

    def set_tn_report(self, report_file):
        """Update trial network report"""
        with open(report_file, "r") as file:
            markdown_content = file.read()
        self.tn_report = markdown_content
    
    def set_deployment_job_name(self, deployment_job_name):
        """Set pipeline use to deploy trial network"""
        self.deployment_job_name = deployment_job_name
    
    def set_destroy_job_name(self, destroy_job_name):
        """Set pipeline use to destroy trial network"""
        self.destroy_job_name = destroy_job_name

    def set_deployment_site(self, deployment_site):
        """Set deployment site to deploy trial network"""
        self.deployment_site = deployment_site

    def set_github_6g_library_commit_id(self, github_6g_library_commit_id):
        """Set commit id from 6G-Library to be used for deploy trial network"""
        self.github_6g_library_commit_id = github_6g_library_commit_id

    def set_github_6g_sandbox_sites_commit_id(self, github_6g_sandbox_sites_commit_id):
        """Set commit id from 6G-Sandbox-Sites to be used for deploy trial network"""
        self.github_6g_sandbox_sites_commit_id = github_6g_sandbox_sites_commit_id

    def set_tn_deployed_descriptor(self, tn_deployed_descriptor=None):
        """Set deployed descriptor"""
        if not tn_deployed_descriptor:
            self.tn_deployed_descriptor = self.tn_sorted_descriptor
        else:
            self.tn_deployed_descriptor = self.descriptor_to_json({"trial_network": tn_deployed_descriptor})

    def validate_descriptor(self, list_site_available_components, input):
        """
        Validate descriptor:
        1) Check if the descriptor follows the correct scheme
            1.1) It starts with trial_network and there is only that key
            1.2) Entity names are not empty
            1.3) Check that each entity has a type, dependencies, input and name part if required
            1.4) Check that the value of each part is a correct object (str, list and dict)
            1.5) Check that the value of the type is a component type of the 6G-Library
            1.6) Check whether custom name is required or not depending on the component type
            1.7) Check that custom name has valid characters: a-z, A-Z, 0-9 and _
            1.8) Check that the entity name follows the format: type-name
        2) Check if the component contains the inputs correctly
            2.1) Check that the fields that are mandatory are present
            2.2) The type of the fields is verified
                2.2.1) If it is a choice, it is checked that it is within the possible values
                2.2.2) If it is str, int, list
                2.2.3) If it is a component
            2.3) It is checked the fields that are required_when
        """
        log_handler.info(f"Start validation of the trial network descriptor '{self.tn_id}'")
        tn_raw_descriptor = self.json_to_descriptor(self.tn_raw_descriptor)
        if len(tn_raw_descriptor.keys()) > 1 or "trial_network" not in tn_raw_descriptor:
            raise TrialNetworkInvalidDescriptorError("Trial network descriptor must start with 'trial_network' key", 422)
        tn_descriptor = tn_raw_descriptor["trial_network"]
        for entity_name, entity_data in tn_descriptor.items():
            if len(entity_name) <= 0:
                raise TrialNetworkInvalidDescriptorError(f"There is an empty entity name in the trial network", 422)
            if not isinstance(entity_data, dict) or len(entity_data) == 0 or not set(REQUIRED_FIELDS_DESCRIPTOR).issubset(entity_data.keys()):
                raise TrialNetworkInvalidDescriptorError(f"Following fields are required in each entity of the descriptor: {', '.join(REQUIRED_FIELDS_DESCRIPTOR)}", 422)
            for rfd in REQUIRED_FIELDS_DESCRIPTOR:
                if rfd == "type" and not isinstance(entity_data[rfd], str):
                    raise TrialNetworkInvalidDescriptorError(f"Value of the '{rfd}' key must be a string in the '{entity_name}' entity of the descriptor", 422)
                elif rfd == "dependencies" and not isinstance(entity_data[rfd], list):
                    raise TrialNetworkInvalidDescriptorError(f"Value of the '{rfd}' key must be a list in the '{entity_name}' entity of the descriptor", 422)
                elif rfd == "input" and not isinstance(entity_data[rfd], dict):
                    raise TrialNetworkInvalidDescriptorError(f"Value of the '{rfd}' key must be a dictionary in the '{entity_name}' entity of the descriptor", 422)
            component_type = entity_data["type"]
            if component_type not in list_site_available_components:
                raise TrialNetworkInvalidDescriptorError(f"Component '{component_type}' not available on the '{self.deployment_site}' site", 404)
            log_handler.info(f"Component '{component_type}' is on '{self.deployment_site}' site")
            custom_name = None
            if component_type not in COMPONENTS_EXCLUDE_CUSTOM_NAME:
                if "name" not in entity_data:
                    raise TrialNetworkInvalidDescriptorError(f"Key 'name' is required in definition of '{entity_name}' in descriptor", 422)
                custom_name = entity_data["name"]
            if not custom_name and entity_name not in COMPONENTS_EXCLUDE_CUSTOM_NAME:
                raise TrialNetworkInvalidDescriptorError(f"Entity name has to be equal to the name of one of the following types {', '.join(COMPONENTS_EXCLUDE_CUSTOM_NAME)}", 422)
            if custom_name:
                if not isinstance(custom_name, str):
                    raise TrialNetworkInvalidDescriptorError("Entity name field has to be a string", 422)
                pattern = re.compile(r"^[a-zA-Z0-9_]+$")
                if not pattern.match(custom_name):
                    raise TrialNetworkInvalidDescriptorError(f"Entity name field has to be a string between a-z, A-Z, 0-9 or _", 422)
                if entity_name != f"{component_type}-{custom_name}":
                    raise TrialNetworkInvalidDescriptorError(f"Entity name has to be in the following format: type-name", 422)
            input_sixg_library_component = input[component_type]
            input_descriptor_component = entity_data["input"]
            if len(input_sixg_library_component) == 0 and len(input_descriptor_component) > 0:
                raise TrialNetworkInvalidDescriptorError(f"Invalid input part of '{component_type}' component", 422)
            if len(input_sixg_library_component) > 0:
                for input_sixg_library_key, input_sixg_library_value in input_sixg_library_component.items():
                    sixg_library_required_when = input_sixg_library_value["required_when"]
                    if not isinstance(sixg_library_required_when, bool) and not isinstance(sixg_library_required_when, str):
                        raise TrialNetworkInvalidDescriptorError(f"Component '{component_type}'. The 'required_when' condition for the '{input_sixg_library_key}' input field must be either a bool or a str representing a logical condition.", 422)
                    if eval(str(sixg_library_required_when), {}, input_descriptor_component) and input_sixg_library_key not in input_descriptor_component:
                        raise TrialNetworkInvalidDescriptorError(f"Component '{component_type}'. Field '{input_sixg_library_key}' is mandatory in descriptor when condition '{sixg_library_required_when}' is met", 422)
                    if input_sixg_library_key in input_descriptor_component:
                        sixg_library_type = input_sixg_library_value["type"]
                        # Maybe map is required because the type will be in str, like this 'str'
                        # if not isinstance(input_descriptor_component[input_sixg_library_key], sixg_library_type):
                        #     raise TrialNetworkInvalidDescriptorError(f"Component '{component_type}'. Type of the '{input_sixg_library_key}' field must be '{sixg_library_type}'")
                        if "choices" in input_sixg_library_value:
                            sixg_library_choices = input_sixg_library_value["choices"]
                            if not input_descriptor_component[input_sixg_library_key] in sixg_library_choices:
                                raise TrialNetworkInvalidDescriptorError(f"Component '{component_type}'. Value of the '{input_sixg_library_key}' field must be '{sixg_library_choices}'", 422)
        log_handler.info(f"End validation of the trial network descriptor '{self.tn_id}'")

    def descriptor_to_json(self, descriptor):
        """Convert descriptor to json"""
        return dumps(descriptor)

    def json_to_descriptor(self, descriptor):
        """Convert descriptor in json to Python object"""
        return loads(descriptor)

    def to_dict(self):
        return {
            "user_created": self.user_created,
            "tn_id": self.tn_id,
            "deployment_site": self.deployment_site,
            "github_6g_library_commit_id": self.github_6g_library_commit_id,
            "github_6g_sandbox_sites_commit_id": self.github_6g_sandbox_sites_commit_id
        }
    
    def to_dict_full(self):
        return {
            "user_created": self.user_created,
            "tn_id": self.tn_id,
            "tn_state": self.tn_state,
            "tn_date_created_utc": self.tn_date_created_utc.isoformat(),
            "tn_raw_descriptor": self.json_to_descriptor(self.tn_raw_descriptor),
            "tn_sorted_descriptor": self.json_to_descriptor(self.tn_sorted_descriptor),
            "tn_deployed_descriptor": self.json_to_descriptor(self.tn_deployed_descriptor),
            "tn_report": self.tn_report,
            "deployment_job_name": self.deployment_job_name,
            "destroy_job_name": self.destroy_job_name,
            "deployment_site": self.deployment_site,
            "github_6g_library_commit_id": self.github_6g_library_commit_id,
            "github_6g_sandbox_sites_commit_id": self.github_6g_sandbox_sites_commit_id
        }

    def __repr__(self):
        return "<TrialNetwork #%s>" % (self.tn_id)