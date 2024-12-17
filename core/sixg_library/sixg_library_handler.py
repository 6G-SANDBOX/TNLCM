import os

from conf import SixGLibrarySettings
from core.repository.repository_handler import RepositoryHandler
from core.utils.file_handler import load_yaml
from core.exceptions.exceptions_handler import CustomSixGLibraryException

class SixGLibraryHandler:

    def __init__(
        self,
        https_url: str = None,
        reference_type: str = None, 
        reference_value: str = None,
        directory_path: str = None
    ) -> None:
        """
        Constructor
        
        :param reference_type: type of reference (branch, tag, commit) to switch, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to switch, ``str``
        :param directory_path: directory path into which the 6G-Library is to be cloned, ``str``
        """
        self.github_6g_library_https_url = https_url
        if https_url is None:
            self.github_6g_library_https_url = SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL
        self.github_6g_library_repository_name = SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME
        self.github_6g_library_local_directory = os.path.join(directory_path, self.github_6g_library_repository_name)
        self.github_6g_library_reference_type = reference_type
        self.github_6g_library_reference_value = reference_value
        if reference_type == "branch" and reference_value:
            self.github_6g_library_reference_value = reference_value
        elif reference_type == "commit" and reference_value:
            self.github_6g_library_reference_value = reference_value
        elif reference_type == "tag" and reference_value:
            self.github_6g_library_reference_value = f"refs/tags/{reference_value}"
        else:
            self.github_6g_library_reference_type = "branch"
            self.github_6g_library_reference_value = SixGLibrarySettings.GITHUB_6G_LIBRARY_BRANCH
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_library_https_url, github_repository_name=self.github_6g_library_repository_name, github_local_directory=self.github_6g_library_local_directory, github_reference_type=self.github_6g_library_reference_type, github_reference_value=self.github_6g_library_reference_value)
        self.github_6g_library_commit_id = None

    def git_clone(self) -> None:
        """
        Git clone
        """
        self.repository_handler.git_clone()
    
    def git_checkout(self) -> None:
        """
        Git checkout
        """
        self.repository_handler.git_checkout()
    
    def git_switch(self) -> None:
        """
        Git switch
        """
        self.repository_handler.git_switch()
        self.github_6g_library_commit_id = self.repository_handler.github_commit_id

    def git_branches(self) -> list[str]:
        """
        Git branches

        :return: list with 6G-Library branches, ``list[str]``
        """
        return self.repository_handler.git_branches()
    
    def git_tags(self) -> list[str]:
        """
        Git tags

        :return: list with 6G-Library tags, ``list[str]``
        """
        return self.repository_handler.git_tags()
    
    def get_components(self) -> set:
        """
        Function to get the available components in the 6G-Library
        
        :return components: the available components, ``set``
        """
        components = set()
        if not os.path.isdir(self.github_6g_library_local_directory):
            raise CustomSixGLibraryException(f"Folder of the components is not created in commit {self.github_6g_library_commit_id} of 6G-Library", 404)
        for component in os.listdir(self.github_6g_library_local_directory):
            components.add(component)
        return components
    
    def is_component(self, component_type: str) -> None:
        """
        Function to check if component in the descriptor are in the library
        
        :param component_type: the component type to validate, ``str``
        :raise CustomSixGLibraryException:
        """
        if component_type not in self.get_components():
            raise CustomSixGLibraryException(f"Component {component_type} not found in 6G-Library", 404)
    
    def get_component_input(self, component_type: str) -> dict:
        """
        Function to get the input part of the component types
        
        :param component_type: the component type to get the input part, ``str``
        :return component_input: the input part of the component types, ``dict``
        :raise CustomSixGLibraryException:
        """
        component_input = {}
        public_file_path = os.path.join(self.github_6g_library_local_directory, component_type, ".tnlcm", "public.yaml")
        if not os.path.exists(public_file_path):
            raise CustomSixGLibraryException(f"File {public_file_path} not found", 404)
        
        public_data = load_yaml(file_path=public_file_path)
        if public_data and "input" in public_data:
            component_input = public_data["input"]
        
        return component_input
    
    def get_component_metadata(self, component_type: str) -> dict:
        """
        Function to get the metadata part of the component types
        
        :param component_type: the component type to get the metadata part, ``str``
        :return component_metadata: the metadata part of the component types, ``dict``
        :raise CustomSixGLibraryException:
        """
        component_metadata = {}
        public_file_path = os.path.join(self.github_6g_library_local_directory, component_type, ".tnlcm", "public.yaml")
        if not os.path.exists(public_file_path):
            raise CustomSixGLibraryException(f"File {public_file_path} not found", 404)
        
        public_data = load_yaml(file_path=public_file_path)
        if public_data and "metadata" in public_data:
            component_metadata = public_data["metadata"]
        
        return component_metadata