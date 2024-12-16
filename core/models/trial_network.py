import os

from datetime import datetime, timezone
from string import ascii_lowercase, digits
from random import choice
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from mongoengine import Document, StringField, DictField, DateTimeField

from core.utils.file_handler import load_file
from core.utils.parser_handler import yaml_to_dict
from core.exceptions.exceptions_handler import CustomTrialNetworkException

STATE_MACHINE = {"validated", "suspended", "activated", "failed", "destroyed"}
COMPONENTS_EXCLUDE_CUSTOM_NAME = {"tn_init", "tn_vxlan", "tn_bastion", "tsn"}
REQUIRED_FIELDS_DESCRIPTOR = {"type", "dependencies", "input"}

class TrialNetworkModel(Document):

    user_created = StringField(max_length=100)
    tn_id = StringField(max_length=15, unique=True)
    state = StringField(max_length=50)
    date_created_utc = DateTimeField(default=datetime.now(timezone.utc))
    raw_descriptor = DictField(default={})
    sorted_descriptor = DictField(default={})
    deployed_descriptor = DictField(default={})
    report = StringField()
    directory_path = StringField()
    jenkins_deploy_pipeline = StringField()
    jenkins_destroy_pipeline = StringField()
    deployment_site = StringField()
    input = DictField(default={})
    output = DictField(default={})
    github_6g_library_https_url = StringField()
    github_6g_library_commit_id = StringField()
    github_6g_sandbox_sites_https_url = StringField()
    github_6g_sandbox_sites_commit_id = StringField()

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "trial_network",
        "description": "This collection stores information about trial networks"
    }

    def set_user_created(self, user_created: str) -> None:
        """
        User that create the trial network

        :param user_created: username, `str`
        """
        self.user_created = user_created

    def set_tn_id(self, size: int = 6, chars: str = ascii_lowercase+digits, tn_id: str = None) -> None:
        """
        Generate and set a random tn_id using characters [a-z][0-9]
        
        :param size: length of the generated part of the tn_id, excluding the initial character (default: 6), ``int``
        :param chars: characters to use for generating the tn_id (default: lowercase letters and digits), ``str``
        :param tn_id: an optional tn_id to set. If not provided, a random tn_id will be generated, ``str``
        :raise CustomTrialNetworkException:
        """
        if not tn_id:
            while True:
                random_tn_id = choice(ascii_lowercase) + ''.join(choice(chars) for _ in range(size))
                if not TrialNetworkModel.objects(tn_id=random_tn_id):
                    self.tn_id = random_tn_id
                    break
        else:
            if bool(TrialNetworkModel.objects(tn_id=tn_id)):
                raise CustomTrialNetworkException(f"Trial network with tn_id {tn_id} already exists", 409)
            if not tn_id[0].isalpha():
                raise CustomTrialNetworkException(f"The tn_id has to start with a character (a-z)", 400)
            self.tn_id = tn_id

    def set_directory_path(self, directory_path: str) -> None:
        """
        Set the trial network directory where all information will save

        :param directory_path: path to the trial network directory, ``str``
        """
        os.makedirs(directory_path)
        os.makedirs(os.path.join(directory_path, "input"))
        os.makedirs(os.path.join(directory_path, "output"))
        self.directory_path = directory_path

    def set_state(self, state: str) -> None:
        """
        Set state of trial network
        
        :param state: new state to set for the trial network, ``str``
        :raise CustomTrialNetworkException:
        """
        if state not in STATE_MACHINE:
            raise CustomTrialNetworkException(f"Trial network state {state} not found", 404)
        self.state = state

    def set_descriptor(self, file: FileStorage) -> None:
        """
        Set the trial network raw descriptor from a file
        
        :param file: descriptor file containing YAML data, ``FileStorage``
        :raises CustomTrialNetworkException:
        """
        filename = secure_filename(file.filename)
        if "." not in filename or filename.split(".")[-1].lower() not in ["yml", "yaml"]:
            raise CustomTrialNetworkException("Invalid descriptor format. Only yml or yaml files will be further processed", 422)
        self.raw_descriptor = yaml_to_dict(file.stream)

        entities = self.raw_descriptor["trial_network"]
        ordered_entities = {}

        def dfs(entity):
            if entity not in entities.keys():
                raise CustomTrialNetworkException("Name of the dependency does not match the name of some entity defined in the descriptor", 404)
            if entity in ordered_entities:
                return
            if "dependencies" in entities[entity]:
                for dependency in entities[entity]["dependencies"]:
                    dfs(dependency)
            ordered_entities[entity] = entities[entity]

        for entity in entities:
            dfs(entity)
        
        sorted_descriptor = {"trial_network": ordered_entities}
        deployed_descriptor = {"trial_network": ordered_entities}
        self.sorted_descriptor = sorted_descriptor
        self.deployed_descriptor = deployed_descriptor

    def set_report(self, file_path: str) -> None:
        """
        Set the trial network report from a markdown file

        :param file_path: path to the markdown report file, ``str``
        """
        self.report = load_file(file_path=file_path, mode="rt", encoding="utf-8")
    
    def set_jenkins_deploy_pipeline(self, jenkins_deploy_pipeline: str) -> None:
        """
        Set pipeline use to deploy trial network
        
        :param jenkins_deploy_pipeline: new name of the deployment pipeline, ``str``
        """
        self.jenkins_deploy_pipeline = jenkins_deploy_pipeline
    
    def set_jenkins_destroy_pipeline(self, jenkins_destroy_pipeline: str) -> None:
        """
        Set pipeline use to destroy trial network
        
        :param jenkins_destroy_pipeline: new name of the destroy pipeline, ``str``
        """
        self.jenkins_destroy_pipeline = jenkins_destroy_pipeline

    def set_deployment_site(self, deployment_site: str) -> None:
        """
        Set deployment site to deploy trial network
        
        :param deployment_site: trial network deployment site, ``str``
        """
        self.deployment_site = deployment_site

    def set_input(self, entity_name: str, entity_data_input: dict) -> None:
        """
        Set input parameters used for the entity name

        :param entity_name: name of the entity, ``str``
        :param entity_data_input: dictionary of input parameters for the entity, ``dict``
        """
        self.input[entity_name] = entity_data_input
    
    def set_output(self, entity_name: str, entity_data_output: dict) -> None:
        """
        Set output received by Jenkins

        :param entity_name: name of the entity, ``str``
        :param entity_data_output: dictionary of output message received by Jenkins, ``dict``
        """
        self.output[entity_name] = entity_data_output
    
    def set_github_6g_library_https_url(self, github_6g_library_https_url: str) -> None:
        """
        Set HTTPS URL from 6G-Library to be used for deploy trial network
        
        :param github_6g_library_https_url: HTTPS URL from 6G-Library, ``str``
        """
        self.github_6g_library_https_url = github_6g_library_https_url
    
    def set_github_6g_library_commit_id(self, github_6g_library_commit_id: str) -> None:
        """
        Set commit id from 6G-Library to be used for deploy trial network
        
        :param github_6g_library_commit_id: commit ID from 6G-Library, ``str``
        """
        self.github_6g_library_commit_id = github_6g_library_commit_id
    
    def set_github_6g_sandbox_sites_https_url(self, github_6g_sandbox_sites_https_url: str) -> None:
        """
        Set HTTPS URL from 6G-Sandbox-Sites to be used for deploy trial network
        
        :param github_6g_sandbox_sites_https_url: HTTPS URL from 6G-Sandbox-Sites, ``str``
        """
        self.github_6g_sandbox_sites_https_url = github_6g_sandbox_sites_https_url

    def set_github_6g_sandbox_sites_commit_id(self, github_6g_sandbox_sites_commit_id: str) -> None:
        """
        Set commit id from 6G-Sandbox-Sites to be used for deploy trial network
        
        :param github_6g_sandbox_sites_commit_id: commit ID from 6G-Sandbox-Sites, ``str``
        """
        self.github_6g_sandbox_sites_commit_id = github_6g_sandbox_sites_commit_id

    def set_deployed_descriptor(self, deployed_descriptor: dict = None) -> None:
        """
        Set deployed descriptor
        
        :param deployed_descriptor: deployed descriptor, ``dict``
        """
        if not deployed_descriptor:
            self.deployed_descriptor = self.sorted_descriptor
        else:
            self.deployed_descriptor = {"trial_network": deployed_descriptor}

    def get_components_types(self) -> set:
        """
        Function to get the components types that are in the descriptor

        :return: set with components that compose trial network descriptor, ``set``
        """
        component_types = set()
        tn_descriptor = self.sorted_descriptor["trial_network"]
        for _, component in tn_descriptor.items():
            component_types.add(component["type"])
        return component_types
    
    def validate_descriptor(self, sixg_library_handler, sixg_sandbox_sites_handler) -> None:
        """
        Function to validate the descriptor
        
        :param sixg_library_handler: 6G-Library handler, ``SixGLibraryHandler``
        :param sixg_sandbox_sites_handler: 6G-Sandbox-Sites handler, ``SixGSandboxSitesHandler``
        :raise CustomTrialNetworkException:
        """
        if len(self.raw_descriptor) == 0:
            raise CustomTrialNetworkException("Descriptor is empty", 422)
        if "trial_network" not in self.raw_descriptor:
            raise CustomTrialNetworkException("Descriptor does not contain trial_network", 422)
        if self.raw_descriptor["trial_network"] is None:
            raise CustomTrialNetworkException("Descriptor does not contain any entity", 422)
        for entity_name, entity_data in self.raw_descriptor["trial_network"].items():
            if not isinstance(entity_name, str):
                raise CustomTrialNetworkException("Entity name has to be a string", 422)
            if entity_name == "":
                raise CustomTrialNetworkException("Entity name is empty", 422)
            if not isinstance(entity_data, dict):
                raise CustomTrialNetworkException(f"Data of entity {entity_name} has to be a dictionary", 422)
            if entity_data == {}:
                raise CustomTrialNetworkException(f"Entity {entity_name} has empty data", 422)
            for key in REQUIRED_FIELDS_DESCRIPTOR:
                if key not in entity_data:
                    raise CustomTrialNetworkException(f"Entity {entity_name} does not contain the field {key}", 422)
            component_type = entity_data["type"]
            component_dependencies = entity_data["dependencies"]
            component_input = entity_data["input"]
            if not isinstance(component_type, str):
                raise CustomTrialNetworkException(f"Entity {entity_name} does not contain a type", 422)
            if component_type == "":
                raise CustomTrialNetworkException(f"Entity {entity_name} does not contain a valid type", 422)
            if not isinstance(component_dependencies, list):
                raise CustomTrialNetworkException(f"Entity {entity_name} does not contain dependencies", 422)
            if not isinstance(component_input, dict):
                raise CustomTrialNetworkException(f"Entity {entity_name} does not contain input", 422)
            if component_type in COMPONENTS_EXCLUDE_CUSTOM_NAME:
                if "name" in entity_data:
                    raise CustomTrialNetworkException(f"Entity {entity_name} does not require a name", 422)
            else:
                if "name" not in entity_data:
                    raise CustomTrialNetworkException(f"Entity {entity_name} does not contain a name", 422)
                name = entity_data["name"]
                if not isinstance(name, str):
                    raise CustomTrialNetworkException(f"Entity {entity_name} does not contain a valid name", 422)
                if name == "":
                    raise CustomTrialNetworkException(f"Entity {entity_name} is empty", 422)
                if entity_name != f"{component_type}-{name}":
                    raise CustomTrialNetworkException(f"Entity {entity_name} does not match with the name provided {component_type}-{name}", 422)
            sixg_library_handler.is_component_library(component_type)
            sixg_sandbox_sites_handler.is_component_site(self.deployment_site, component_type)
        if "tn_init" not in self.raw_descriptor["trial_network"] and ("tn_vxlan" not in self.raw_descriptor["trial_network"] and "tn_bastion" not in self.raw_descriptor["trial_network"]):
            raise CustomTrialNetworkException("Descriptor does not contain the required entities tn_init or tn_vxlan and tn_bastion", 422)
        # TODO: input validation
        
    def to_dict(self) -> dict:
        return {
            "user_created": self.user_created,
            "tn_id": self.tn_id,
            "state": self.state,
            "deployment_site": self.deployment_site,
            "directory_path": self.directory_path,
            "github_6g_library_https_url": self.github_6g_library_https_url,
            "github_6g_library_commit_id": self.github_6g_library_commit_id,
            "github_6g_sandbox_sites_https_url": self.github_6g_sandbox_sites_https_url,
            "github_6g_sandbox_sites_commit_id": self.github_6g_sandbox_sites_commit_id
        }
    
    def to_dict_full(self) -> dict:
        return {
            "user_created": self.user_created,
            "tn_id": self.tn_id,
            "state": self.state,
            "date_created_utc": self.date_created_utc.isoformat(),
            "raw_descriptor": self.raw_descriptor,
            "sorted_descriptor": self.sorted_descriptor,
            "deployed_descriptor": self.deployed_descriptor,
            "report": self.report,
            "directory_path": self.directory_path,
            "jenkins_deploy_pipeline": self.jenkins_deploy_pipeline,
            "jenkins_destroy_pipeline": self.jenkins_destroy_pipeline,
            "deployment_site": self.deployment_site,
            "input": self.input,
            "output": self.output,
            "github_6g_library_https_url": self.github_6g_library_https_url,
            "github_6g_library_commit_id": self.github_6g_library_commit_id,
            "github_6g_sandbox_sites_https_url": self.github_6g_sandbox_sites_https_url,
            "github_6g_sandbox_sites_commit_id": self.github_6g_sandbox_sites_commit_id
        }

    def __repr__(self) -> str:
        return "<TrialNetwork #%s>" % (self.tn_id)