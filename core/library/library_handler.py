from typing import Dict, List

from conf.library import LibrarySettings
from core.exceptions.exceptions import LibraryError
from core.libs.git import Git
from core.utils.file import load_yaml
from core.utils.os import (
    get_absolute_path,
    is_directory,
    is_file,
    join_path,
    list_dirs_no_hidden,
    list_files_no_hidden,
)

LIBRARY_PATH = join_path(
    get_absolute_path(__file__), LibrarySettings.LIBRARY_REPOSITORY_NAME
)
LIBRARY_REFERENCES_TYPES = ["branch", "commit", "tag"]


class LibraryHandler:
    def __init__(
        self,
        https_url: str = None,
        reference_type: str = None,
        reference_value: str = None,
        directory_path: str = None,
    ) -> None:
        """
        Constructor

        :param https_url: URL of the repository, ``str``
        :param reference_type: type of reference (branch, tag, commit) to switch, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to switch, ``str``
        :param directory_path: directory path into which the Library is to be cloned, ``str``
        """
        self.library_https_url = https_url
        if https_url is None:
            self.library_https_url = LibrarySettings.LIBRARY_HTTPS_URL
        self.library_repository_name = LibrarySettings.LIBRARY_REPOSITORY_NAME
        if directory_path is None:
            self.library_local_directory = LIBRARY_PATH
        else:
            self.library_local_directory = join_path(
                directory_path, self.library_repository_name
            )
        self.library_reference_type = reference_type
        self.library_reference_value = reference_value
        if reference_type == "branch" and reference_value:
            self.library_reference_value = reference_value
        elif reference_type == "commit" and reference_value:
            self.library_reference_value = reference_value
        elif reference_type == "tag" and reference_value:
            self.library_reference_value = f"tags/{reference_value}"
        else:
            self.library_reference_type = "branch"
            self.library_reference_value = LibrarySettings.LIBRARY_BRANCH
        self.git_client = Git(
            github_https_url=self.library_https_url,
            github_repository_name=self.library_repository_name,
            github_local_directory=self.library_local_directory,
            github_reference_type=self.library_reference_type,
            github_reference_value=self.library_reference_value,
        )
        self.library_commit_id = None

    def branches(self) -> List[str]:
        """
        Function to get the branches of the Library

        :return branches: the branches of the Library, ``List[str]``
        """
        branches = self.git_client.branches()
        if "assets" in branches:
            branches.remove("assets")
        return branches

    def get_component(self, component_name: str) -> Dict:
        """
        Function to get the component type

        :param component_name: the component type to get, ``str``
        :return component: the component type, ``Dict``
        :raise LibraryError:
        """
        component = {}
        self.is_component_library(component_name=component_name)
        public_file_path = join_path(
            self.library_local_directory, component_name, ".tnlcm", "public.yaml"
        )
        if not is_file(path=public_file_path):
            raise LibraryError(
                message=f"File {public_file_path} not found in {component_name} component in {self.library_reference_type} reference type and {self.library_reference_value} reference value",
                status_code=404,
            )
        public_data = load_yaml(file_path=public_file_path)
        if public_data:
            component = public_data
        return component

    def get_component_input(self, component_name: str) -> Dict:
        """
        Function to get the input part of the component types

        :param component_name: the component type to get the input part, ``str``
        :return component_input: the input part of the component type, ``Dict``
        :raise LibraryError:
        """
        component_input = {}
        public_file_path = join_path(
            self.library_local_directory, component_name, ".tnlcm", "public.yaml"
        )
        if not is_file(path=public_file_path):
            raise LibraryError(
                message=f"File {public_file_path} not found in {component_name} component in {self.library_reference_type} reference type and {self.library_reference_value} reference value",
                status_code=404,
            )
        public_data = load_yaml(file_path=public_file_path)
        if public_data and "input" in public_data:
            component_input = public_data["input"]
        return component_input

    def get_component_metadata(self, component_name: str) -> Dict:
        """
        Function to get the metadata part of the component types

        :param component_name: the component type to get the metadata part, ``str``
        :return component_metadata: the metadata part of the component type, ``Dict``
        :raise LibraryError:
        """
        component_metadata = {}
        public_file_path = join_path(
            self.library_local_directory, component_name, ".tnlcm", "public.yaml"
        )
        if not is_file(path=public_file_path):
            raise LibraryError(
                message=f"File {public_file_path} not found in {component_name} component in {self.library_reference_type} reference type and {self.library_reference_value} reference value",
                status_code=404,
            )
        public_data = load_yaml(file_path=public_file_path)
        if public_data and "metadata" in public_data:
            component_metadata = public_data["metadata"]
        return component_metadata

    def get_components(self) -> List[str]:
        """
        Function to get the available components in the Library

        :return components: the available components, ``List[str]``
        :raise LibraryError:
        """
        components = []
        if not is_directory(path=self.library_local_directory):
            raise LibraryError(
                message=f"No components available in {self.library_reference_type} reference type and {self.library_reference_value} reference value",
                status_code=404,
            )
        for component in list_dirs_no_hidden(path=self.library_local_directory):
            if is_directory(
                path=join_path(self.library_local_directory, component)
            ) and not component.startswith("."):
                components.append(component)
        return sorted(components)

    def get_trial_networks_templates_component(self, component_name: str) -> Dict:
        """
        Function to get the trial networks template of the component type

        :param component_name: the component type to get the trial networks template, ``str``
        :return trial_networks_templates: the trial networks template, ``Dict``
        :raise LibraryError:
        """
        trial_networks_templates = {}
        component_path = join_path(self.library_local_directory, component_name)
        component_templates = []
        for file in list_files_no_hidden(path=component_path):
            if file.startswith("sample_tnlcm_descriptor"):
                file_path = join_path(component_path, file)
                file_content = load_yaml(file_path=file_path)
                component_templates.append(file_content)
        trial_networks_templates[component_name] = component_templates
        return trial_networks_templates

    def get_trial_networks_templates(self) -> Dict:
        """
        Function to get the trial networks templates

        :return trial_networks_templates: the trial networks templates, ``Dict``
        """
        components = self.get_components()
        trial_networks_templates = {}
        for component in components:
            trial_networks_templates[component] = (
                self.get_trial_networks_templates_component(component_name=component)
            )
        return trial_networks_templates

    def is_component_library(self, component_name: str) -> None:
        """
        Function to check if component in the descriptor are in the library

        :param component_name: the component type to validate, ``str``
        :raise LibraryError:
        """
        if component_name not in self.get_components():
            raise LibraryError(
                message=f"Component {component_name} not found in {self.library_reference_type} reference type and {self.library_reference_value} reference value",
                status_code=404,
            )
