from werkzeug.utils import secure_filename
from json import dumps, loads
from yaml import safe_load, YAMLError
from string import ascii_lowercase, digits
from random import choice
from datetime import datetime, timezone
from mongoengine import Document, StringField, DateTimeField

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import InvalidFileExtensionError, InvalidContentFileError, TrialNetworkEntityNotInDescriptorError, TrialNetworkInvalidStatusError, TrialNetworkInvalidComponentSiteError, TrialNetworkInvalidInputComponentError

TN_STATE_MACHINE = ["validated", "suspended", "activated", "failed", "destroyed"]

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

    def _validate_input_part(self, component_type, input_sixg_library_component, input_descriptor_component):
        """
        2.1) Check that the fields that are mandatory are present
        """
        log_handler.info(f"Start the validation of the mandatory fields of the '{component_type}' component")
        if len(input_sixg_library_component) == 0 and len(input_descriptor_component) > 0:
            raise TrialNetworkInvalidInputComponentError(f"Input part of '{component_type}' component should be: '{input_sixg_library_component}'", 422)
        if len(input_sixg_library_component) > 0:
            for input_sixg_library_key, input_sixg_library_value in input_sixg_library_component.items():
                sixg_library_required_when = input_sixg_library_value["required_when"]
                if sixg_library_required_when and input_sixg_library_key not in input_descriptor_component:
                    raise TrialNetworkInvalidInputComponentError(f"Field '{input_sixg_library_key}' is mandatory in descriptor", 422)
        log_handler.info(f"End the validation of the mandatory fields of the '{component_type}' component")

    def validate_descriptor(self, list_site_available_components, input):
        """
        Validate descriptor:
        1) Check if the component exists on the site where the component is to be deployed
        2) Check if the component contains the inputs correctly
            2.1) Check that the fields that are mandatory are present
            2.2) The type of the fields is verified
                2.2.1) If it is a choice, it is checked that it is within the possible values
                2.2.2) If it is str, int, list
                2.2.3) If it is a component
            2.3) It is checked the fields that are required_when
        """
        log_handler.info(f"Start validation of the trial network descriptor '{self.tn_id}'")
        tn_descriptor = self.json_to_descriptor(self.tn_sorted_descriptor)["trial_network"]
        for _, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            if component_type not in list_site_available_components:
                raise TrialNetworkInvalidComponentSiteError(f"Component '{component_type}' not available on the '{self.deployment_site}' site", 404)
            log_handler.info(f"Component '{component_type}' is on '{self.deployment_site}' site")
            input_sixg_library_component = input[component_type]
            input_descriptor_component = entity_data["input"]
            self._validate_input_part(component_type, input_sixg_library_component, input_descriptor_component)
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