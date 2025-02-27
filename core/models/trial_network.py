import ast
import re

from datetime import datetime, timezone
from mongoengine import DateTimeField, DictField, Document, StringField
from random import choice
from string import ascii_lowercase, digits
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from core.utils.file_handler import load_file
from core.utils.os_handler import join_path, make_directory
from core.utils.parser_handler import yaml_to_dict
from core.exceptions.exceptions_handler import CustomTrialNetworkException

STATE_MACHINE = {"validated", "suspended", "activated", "failed", "destroyed"}
COMPONENTS_EXCLUDE_CUSTOM_NAME = {"tn_init", "tn_vxlan", "tn_bastion", "tsn"}
REQUIRED_FIELDS_DESCRIPTOR = {"type", "dependencies", "input"}
TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}
OPERATORS = {
    ast.And: lambda x, y: x and y,
    ast.Or: lambda x, y: x or y,
    ast.Eq: lambda x, y: x == y,
    ast.NotEq: lambda x, y: x != y,
    ast.Lt: lambda x, y: x < y,
    ast.LtE: lambda x, y: x <= y,
    ast.Gt: lambda x, y: x > y,
    ast.GtE: lambda x, y: x >= y,
}

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
    library_https_url = StringField()
    library_commit_id = StringField()
    sites_https_url = StringField()
    sites_commit_id = StringField()

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
                raise CustomTrialNetworkException("The tn_id has to start with a character (a-z)", 400)
            self.tn_id = tn_id

    def set_directory_path(self, directory_path: str) -> None:
        """
        Set the trial network directory where all information will save

        :param directory_path: path to the trial network directory, ``str``
        """
        make_directory(path=directory_path)
        make_directory(path=join_path(directory_path, "input"))
        make_directory(path=join_path(directory_path, "output"))
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

    def set_raw_descriptor(self, file: FileStorage) -> None:
        """
        Set the trial network raw descriptor from a file
        
        :param file: descriptor file containing YAML data, ``FileStorage``
        :raises CustomTrialNetworkException:
        """
        filename = secure_filename(file.filename)
        if "." not in filename or filename.split(".")[-1].lower() not in ["yml", "yaml"]:
            raise CustomTrialNetworkException("Invalid descriptor format. Only yml or yaml files will be further processed", 422)
        self.raw_descriptor = yaml_to_dict(file.stream)

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
    
    def set_library_https_url(self, library_https_url: str) -> None:
        """
        Set HTTPS URL from Library to be used for deploy trial network
        
        :param library_https_url: HTTPS URL from Library, ``str``
        """
        self.library_https_url = library_https_url
    
    def set_library_commit_id(self, library_commit_id: str) -> None:
        """
        Set commit id from Library to be used for deploy trial network
        
        :param library_commit_id: commit ID from Library, ``str``
        """
        self.library_commit_id = library_commit_id
    
    def set_sites_https_url(self, sites_https_url: str) -> None:
        """
        Set HTTPS URL from Sites to be used for deploy trial network
        
        :param sites_https_url: HTTPS URL from Sites, ``str``
        """
        self.sites_https_url = sites_https_url

    def set_sites_commit_id(self, sites_commit_id: str) -> None:
        """
        Set commit id from Sites to be used for deploy trial network
        
        :param sites_commit_id: commit ID from Sites, ``str``
        """
        self.sites_commit_id = sites_commit_id

    def set_deployed_descriptor(self, deployed_descriptor: dict = None) -> None:
        """
        Set deployed descriptor
        
        :param deployed_descriptor: deployed descriptor, ``dict``
        """
        if not deployed_descriptor:
            self.deployed_descriptor = self.sorted_descriptor
        else:
            self.deployed_descriptor = {"trial_network": deployed_descriptor}
    
    def _evaluate_expression(self, component_input_library, expression: str, context: dict) -> bool:
        """
        Safely evaluate a boolean expression in the context of a dictionary, ensuring that 
        fields required in the component library are not missing.

        :param component_input_library: input part in Library, ``dict``
        :param expression: The boolean expression to evaluate, ``str``
        :param context: The dictionary providing values for the variables in the expression, ``dict``
        :return: The result of the evaluation, ``bool``
        """

        def _eval(node):
            if isinstance(node, ast.BoolOp):
                op = OPERATORS[type(node.op)]
                return op(_eval(node.values[0]), _eval(node.values[1]))
            elif isinstance(node, ast.BinOp):
                op = OPERATORS[type(node.op)]
                return op(_eval(node.left), _eval(node.right))
            elif isinstance(node, ast.Compare):
                left = _eval(node.left)
                right = _eval(node.comparators[0])
                op = OPERATORS[type(node.ops[0])]
                return op(left, right)
            elif isinstance(node, ast.Name):
                field_name = node.id
                
                # Verificar si el campo es requerido en la librería de componentes
                if field_name in component_input_library:
                    field_info = component_input_library[field_name]
                    if field_info.get("required", False):  # Si el campo es requerido
                        raise ValueError(f"Field '{field_name}' is required but missing in context.")
                
                # Si el campo está en context, devolvemos su valor, si no, asumimos None
                return context.get(field_name, None)
            
            elif isinstance(node, ast.Constant):
                return node.value
            
            raise TypeError(f"Unsupported AST node: {type(node)}")

        tree = ast.parse(expression, mode="eval")
        return _eval(tree.body)

    def _required_when(self, component_input_library, input_required_when: bool | str, component_input: dict) -> bool:
        """
        Function to check if the input is required
        
        :param component_input_library: input part in Library, ``dict``
        :param input_required_when: boolean to check if the input is required, ``bool``
        :param component_input: input provided in the descriptor, ``dict``
        :return: boolean to check if the input is required, ``bool``
        """
        if isinstance(input_required_when, bool):
            return input_required_when
        if isinstance(input_required_when, str):
            return self._evaluate_expression(component_input_library, input_required_when, component_input)
    
    def _isinstance_entity_name(self, input_type: str, input_value: str) -> None:
        """
        Function to check if the input is an entity name
        
        :param input_type: type of the input, ``str``
        :param input_value: value of the input, ``str``
        """
        if input_value == "tn_vxlan":
            if "tn_init" not in self.raw_descriptor["trial_network"]:
                raise CustomTrialNetworkException("Entity tn_vxlan is not allowed without entity tn_init", 422)
        else:
            if input_value not in self.raw_descriptor["trial_network"]:
                raise CustomTrialNetworkException(f"Entity {input_value} not found in the descriptor", 422)
            type_component = self.raw_descriptor["trial_network"][input_value]["type"]
            if type_component not in input_type:
                raise CustomTrialNetworkException(f"Entity {input_value} is not of type {input_type}", 422)
        
    def _isinstance_list(self, input_type: str, input_value: list) -> None:
        """
        Function to check if the input is a list
        
        :param input_type: type of the input, ``str``
        :param input_value: value of the input, ``list``
        """
        input_type = input_type[5:-1]
        for value in input_value:
            self._isinstance_entity_name(input_type, value)
    
    def _boolean_expression(self, input_type: str) -> bool:
        """
        Function to check if the input is a boolean expression
        
        :param input_type: type of the input, ``str``
        :return: boolean to check if the input is a boolean expression, ``bool``
        """
        return bool(re.match(r"^(\w+\s*(and|or)\s*\w+(\s*(and|or)\s*\w+)*)$", input_type))
    
    def _isinstance_component(self, input_type: str, library_handler) -> bool:
        """
        Function to check if the input is a component
        
        :param input_type: type of the input, ``str``
        :param library_handler: Library handler, ``LibraryHandler``
        :return: boolean to check if the input is a component, ``bool``
        """
        return input_type in library_handler.get_components()
    
    def _check_input(self, library_handler, component_input: dict, component_input_library: dict) -> None:
        """
        Function to check if the input provided in the descriptor is correct
        
        :param library_handler: Library handler, ``LibraryHandler``
        :param component_input: input provided in the descriptor, ``dict``
        :param component_input_library: input part in Library, ``dict``
        :raise CustomTrialNetworkException:
        """
        if (component_input_library is None or len(component_input_library) == 0) and len(component_input) > 0:
            raise CustomTrialNetworkException("Input is not allowed", 422)
        if component_input_library is not None:
            for key, value in component_input_library.items():
                if "type" not in value:
                    raise CustomTrialNetworkException(f"Input {key} does not contain type in 6G-Library definition", 422)
                input_type = value["type"]
                if "required_when" not in value:
                    raise CustomTrialNetworkException(f"Input {key} does not contain required_when in 6G-Library definition", 422)
                input_required_when = value["required_when"]
                if self._required_when(component_input_library, input_required_when, component_input) and key not in component_input:
                    raise CustomTrialNetworkException(f"Input {key} is required", 422)
                if key in component_input:
                    if input_type.startswith("list[") and input_type.endswith("]"):
                        self._isinstance_list(input_type, component_input[key])
                    elif self._boolean_expression(input_type):
                        self._isinstance_entity_name(input_type, component_input[key])
                    elif self._isinstance_component(input_type, library_handler):
                        self._isinstance_entity_name(input_type, component_input[key])
                    elif input_type in TYPE_MAPPING and not isinstance(component_input[key], TYPE_MAPPING[input_type]):
                        raise CustomTrialNetworkException(f"Input {key} is not of type", 422)
                    if "choices" in value and component_input[key] not in value["choices"]:
                        choices = value["choices"]
                        raise CustomTrialNetworkException(f"Input {key} has to be one of the following choices {choices}", 422)
    
    def validate_descriptor(self, library_handler, sites_handler) -> None:
        """
        Function to validate the descriptor
        
        :param library_handler: Library handler, ``LibraryHandler``
        :param sites_handler: Sites handler, ``SitesHandler``
        :raise CustomTrialNetworkException:
        """
        if len(self.raw_descriptor) == 0:
            raise CustomTrialNetworkException("Descriptor is empty", 422)
        if "trial_network" not in self.raw_descriptor:
            raise CustomTrialNetworkException("Descriptor does not contain trial_network", 422)
        if self.raw_descriptor["trial_network"] is None:
            raise CustomTrialNetworkException("Descriptor does not contain any entity", 422)
        if "tn_init" not in self.raw_descriptor["trial_network"] and ("tn_vxlan" not in self.raw_descriptor["trial_network"] and "tn_bastion" not in self.raw_descriptor["trial_network"]):
            raise CustomTrialNetworkException("Descriptor does not contain the required entities tn_init or tn_vxlan and tn_bastion", 422)
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
            library_handler.is_component(component_type)
            sites_handler.is_component(self.deployment_site, component_type)
            component_input_library = library_handler.get_component_input(component_type)
            self._check_input(library_handler, component_input, component_input_library)
        
    def to_dict(self) -> dict:
        return {
            "user_created": self.user_created,
            "tn_id": self.tn_id,
            "state": self.state,
            "date_created_utc": self.date_created_utc.isoformat(),
            "deployment_site": self.deployment_site,
            "directory_path": self.directory_path,
            "library_https_url": self.library_https_url,
            "library_commit_id": self.library_commit_id,
            "sites_https_url": self.sites_https_url,
            "sites_commit_id": self.sites_commit_id
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
            "library_https_url": self.library_https_url,
            "library_commit_id": self.library_commit_id,
            "sites_https_url": self.sites_https_url,
            "sites_commit_id": self.sites_commit_id
        }

    def __repr__(self) -> str:
        return "<TrialNetwork #%s>" % (self.tn_id)