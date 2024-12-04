import os
import re

from yaml import safe_load
from datetime import datetime, timezone
from string import ascii_lowercase, digits
from random import choice
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from mongoengine import Document, StringField, DictField, DateTimeField

from core.utils.file_handler import load_file
from core.exceptions.exceptions_handler import CustomTrialNetworkException

STATE_MACHINE = {"validated", "suspended", "activated", "failed", "destroyed"}
COMPONENTS_EXCLUDE_CUSTOM_NAME = {"tn_vxlan", "tn_bastion", "tn_init", "tsn"}
REQUIRED_FIELDS_DESCRIPTOR = {"type", "input"}

class TrialNetworkModel(Document):

    user_created = StringField(max_length=100)
    tn_id = StringField(max_length=15, unique=True)
    state = StringField(max_length=50)
    date_created_utc = DateTimeField(default=datetime.now(timezone.utc))
    raw_descriptor = DictField()
    sorted_descriptor = DictField()
    deployed_descriptor = DictField()
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

    def verify_tn_id(self, tn_id: str) -> bool:
        """
        Verify if tn_id exists in database

        :param tn_id: trial network identifier, ``str``
        :return: True if tn_id is in database. Otherwise False, ``bool``
        """
        return bool(TrialNetworkModel.objects(tn_id=tn_id))

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
            if not tn_id[0].isalpha():
                raise CustomTrialNetworkException(f"The tn_id '{tn_id}' must start with a character (a-z)", 400)
            self.tn_id = tn_id

    def set_state(self, state: str) -> None:
        """
        Set state of trial network
        
        :param state: new state to set for the trial network, ``str``
        :raise CustomTrialNetworkException:
        """
        if state not in STATE_MACHINE:
            raise CustomTrialNetworkException(f"Trial network '{state}' state not found", 404)
        self.state = state

    def set_raw_descriptor(self, file: FileStorage) -> None:
        """
        Set the trial network raw descriptor from a file
        
        :param file: descriptor file containing YAML data, ``FileStorage``
        :raises CustomTrialNetworkException:
        """
        filename = secure_filename(file.filename)
        if "." not in filename or filename.split(".")[-1].lower() not in ["yml", "yaml"]:
            raise CustomTrialNetworkException("Invalid descriptor format. Only 'yml' or 'yaml' files will be further processed", 422)
        self.raw_descriptor = safe_load(file.stream)

    def set_sorted_descriptor(self) -> None:
        """
        Recursive method that return the raw descriptor and a new descriptor sorted according to dependencies

        :raise CustomTrialNetworkException:
        """
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
        
        self.sorted_descriptor = {"trial_network": ordered_entities}
        self.deployed_descriptor = {"trial_network": ordered_entities}

    def set_report(self, file_path: str) -> None:
        """
        Set the trial network report from a markdown file

        :param file_path: path to the markdown report file, ``str``
        """
        self.report = load_file(file_path=file_path, mode="rt", encoding="utf-8")
    
    def set_directory_path(self, directory_path: str) -> None:
        """
        Set the trial network directory where all information will save

        :param directory_path: path to the trial network directory, ``str``
        """
        os.makedirs(directory_path)
        self.directory_path = directory_path
    
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

    def _logical_expression(
        self, 
        tn_components_types: set, 
        bool_expresion: bool, 
        tn_descriptor: dict, 
        component_name: str
    ) -> bool:
        """
        In case the type is a logical expression. For example: tn_vxlan or vnet
        
        :param tn_components_types: set with the components that make up the descriptor, ``set``
        :param bool_expresion: bool expresion to evaluate, ``bool``
        :param tn_descriptor: trial network sorted descriptor, ``dict``
        :param component_name: component name that is in input part of descriptor, ``str``
        :return: result of evaluating whether the component type matches the logical expression, ``bool``
        :raises CustomTrialNetworkException:
        """
        def is_valid_part(part: str) -> bool:
            """
            Check if the part of the logical expression is valid
            
            :param part: part of the logical expression, ``str``
            :return: True if the part is valid. Otherwise False, ``bool``
            """
            part = part.strip()
            cn = component_name
            if (component_name == "tn_vxlan" or component_name == "tn_bastion") and component_name not in tn_descriptor:
                cn = "tn_init"
                part = "tn_init"
            if part not in tn_components_types:
                return False
            if cn not in tn_descriptor:
                return False
            if "type" not in tn_descriptor[cn]:
                return False
            if not tn_descriptor[cn]["type"]:
                return False
            
            return tn_descriptor[cn]["type"] == part
        
        parts = bool_expresion.split(" or ")
        is_valid = False
        for part in parts:
            if is_valid_part(part):
                is_valid = True
                break

        if not is_valid:
            raise CustomTrialNetworkException(f"The boolean expression '{bool_expresion}' does not match any valid component type", 422)

        return is_valid
    
    def _validate_list_of_networks(
        self, 
        tn_components_types: set, 
        bool_expresion: bool, 
        tn_descriptor: dict, 
        component_list: list[str]
    ) -> None:
        """
        Validates a list of networks with logical expression. For example: list[tn_vxlan or vnet]
        
        :param tn_components_types: set with the components that make up the descriptor, ``set``
        :param bool_expresion: boolean expression to evaluate, ``bool``
        :param tn_descriptor: trial network sorted descriptor, ``dict``
        :param component_list: list of components that are in the input part of the descriptor, ``list[str]``
        :raises CustomTrialNetworkException:
        """
        for component_name in component_list:
            if not isinstance(component_name, str):
                raise CustomTrialNetworkException(f"Component name '{component_name}' in the list must be a string", 422)
            if not self._logical_expression(tn_components_types, bool_expresion, tn_descriptor, component_name):
                raise CustomTrialNetworkException(f"Component '{component_name}' in the list does not match the type '{bool_expresion}'", 422)

    def validate_descriptor(self, tn_components_types: set, tn_component_inputs: dict) -> None:
        """
        If the descriptor follows the correct scheme
        It starts with trial_network and there is only that key
        Entity names are not empty
        Check that each entity has a type, dependencies, input and name part if required
        Check that the value of each part is a correct object (str, list and dict)
        Check whether custom name is required or not depending on the component type
        Check that custom name has valid characters: [a-zA-Z0-9_]
        Check that the entity name follows the format: type-name
        Check if the component contains the inputs correctly
        Check that the fields that are mandatory are present
        The type of the fields is verified
        If it is a choice, it is checked that it is within the possible values
        If it is str, int, list
        If it is a component
        It is checked the fields that are required_when

        :param tn_components_types: set with the components that make up the descriptor, ``set``
        :param tn_component_inputs: correct component inputs from the 6G-Library, ``dict``
        :raises CustomTrialNetworkException:
        """
        if len(self.raw_descriptor.keys()) > 1 or "trial_network" not in self.raw_descriptor:
            raise CustomTrialNetworkException("Trial network descriptor must start with 'trial_network' key", 422)
        tn_descriptor = self.raw_descriptor["trial_network"]
        if "tn_init" in tn_components_types:
            tn_components_types.add("tn_vxlan")
            tn_components_types.add("tn_bastion")
        if "tn_vxlan" in tn_components_types and "tn_bastion" in tn_components_types:
            tn_components_types.add("tn_init")
        for entity_name, entity_data in tn_descriptor.items():
            if len(entity_name) <= 0:
                raise CustomTrialNetworkException(f"There is an empty entity name in the trial network", 422)
            if not isinstance(entity_data, dict) or len(entity_data) == 0 or not set(REQUIRED_FIELDS_DESCRIPTOR).issubset(entity_data.keys()):
                raise CustomTrialNetworkException(f"Following fields are required in each entity of the descriptor: {', '.join(REQUIRED_FIELDS_DESCRIPTOR)}", 422)
            for rfd in REQUIRED_FIELDS_DESCRIPTOR:
                if rfd == "type" and not isinstance(entity_data[rfd], str):
                    raise CustomTrialNetworkException(f"Value of the '{rfd}' key must be a string in the '{entity_name}' entity of the descriptor", 422)
                elif rfd == "dependencies" and not isinstance(entity_data[rfd], list):
                    raise CustomTrialNetworkException(f"Value of the '{rfd}' key must be a list in the '{entity_name}' entity of the descriptor", 422)
                elif rfd == "input" and not isinstance(entity_data[rfd], dict):
                    raise CustomTrialNetworkException(f"Value of the '{rfd}' key must be a dictionary in the '{entity_name}' entity of the descriptor", 422)
            component_type = entity_data["type"]
            custom_name = None
            if component_type not in COMPONENTS_EXCLUDE_CUSTOM_NAME:
                if "name" not in entity_data:
                    raise CustomTrialNetworkException(f"Key 'name' is required in definition of '{entity_name}' in descriptor", 422)
                custom_name = entity_data["name"]
            if not custom_name and entity_name not in COMPONENTS_EXCLUDE_CUSTOM_NAME:
                raise CustomTrialNetworkException(f"Entity name has to be equal to the name of one of the following types {', '.join(COMPONENTS_EXCLUDE_CUSTOM_NAME)}", 422)
            if custom_name:
                if not isinstance(custom_name, str):
                    raise CustomTrialNetworkException("Entity name field has to be a string", 422)
                pattern = re.compile(r"^[a-zA-Z0-9_]+$")
                if not pattern.match(custom_name):
                    raise CustomTrialNetworkException(f"Entity name field has to be a string between a-z, A-Z, 0-9 or _", 422)
                if entity_name != f"{component_type}-{custom_name}":
                    raise CustomTrialNetworkException(f"Entity name has to be in the following format: type-name", 422)
            input_sixg_library_component = tn_component_inputs[component_type]
            input_descriptor_component = entity_data["input"]
            if input_sixg_library_component:
                if len(input_sixg_library_component) == 0 and len(input_descriptor_component) > 0:
                    raise CustomTrialNetworkException(f"Invalid input part of '{component_type}' component", 422)
                if len(input_sixg_library_component) > 0:
                    for input_sixg_library_key, input_sixg_library_value in input_sixg_library_component.items():
                        sixg_library_required_when = input_sixg_library_value["required_when"]
                        if not isinstance(sixg_library_required_when, bool) and not isinstance(sixg_library_required_when, str):
                            raise CustomTrialNetworkException(f"Component '{component_type}'. The 'required_when' condition for the '{input_sixg_library_key}' input field must be either a bool or a str representing a logical condition.", 422)
                        if input_sixg_library_key in input_descriptor_component:
                            sixg_library_type = input_sixg_library_value["type"]
                            type_mapping = {
                                "str": str,
                                "int": int,
                                "bool": bool,
                                "list": list,
                                "dict": dict,
                            }
                            component_name = input_descriptor_component[input_sixg_library_key]
                            if sixg_library_type.startswith("list[") and sixg_library_type.endswith("]"):
                                bool_expresion = sixg_library_type[5:-1]
                                self._validate_list_of_networks(tn_components_types, bool_expresion, tn_descriptor, component_name)
                            else:
                                if sixg_library_type not in type_mapping and sixg_library_type not in tn_components_types and not self._logical_expression(tn_components_types, sixg_library_type, tn_descriptor, component_name):
                                    raise CustomTrialNetworkException(f"Component '{component_type}'. Unknown type '{sixg_library_type}' for the '{input_sixg_library_key}' field", 422)
                                if sixg_library_type in type_mapping:
                                    if not isinstance(input_descriptor_component[input_sixg_library_key], type_mapping[sixg_library_type]):
                                        raise CustomTrialNetworkException(f"Component '{component_type}'. Type of the '{input_sixg_library_key}' field must be '{sixg_library_type}'", 422)
                                elif sixg_library_type in tn_components_types:
                                    if not isinstance(component_name, str):
                                        raise CustomTrialNetworkException(f"Component '{component_type}'. The '{input_sixg_library_key}' field must be a string referring to a component name", 422)
                                    if component_name not in tn_descriptor:
                                        raise CustomTrialNetworkException(f"Component '{component_type}'. The component name '{component_name}' referenced in '{input_sixg_library_key}' does not exist in the descriptor", 422)
                                    if "type" not in tn_descriptor[component_name]:
                                        raise CustomTrialNetworkException(f"Component '{component_type}'. The referenced component '{component_name}' must have a 'type' field", 422)
                                    if not tn_descriptor[component_name]["type"]:
                                        raise CustomTrialNetworkException(f"Component '{component_type}'. The 'type' field of the referenced component '{component_name}' cannot be empty", 422)
                                    if tn_descriptor[component_name]["type"] != sixg_library_type:
                                        raise CustomTrialNetworkException(f"Component '{component_type}'. The component name '{component_name}' referenced in '{input_sixg_library_key}' must be of type '{sixg_library_type}'", 422)
                            if "choices" in input_sixg_library_value:
                                sixg_library_choices = input_sixg_library_value["choices"]
                                if not input_descriptor_component[input_sixg_library_key] in sixg_library_choices:
                                    raise CustomTrialNetworkException(f"Component '{component_type}'. Value of the '{input_sixg_library_key}' field has to be one of then: '{sixg_library_choices}'", 422)

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