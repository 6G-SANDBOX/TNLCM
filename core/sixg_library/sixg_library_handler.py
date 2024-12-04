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
        if not https_url:
            self.github_6g_library_https_url = SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL
        else:
            self.github_6g_library_https_url = https_url
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
    
    def get_tn_components_parts(self, parts: list[str], tn_components_types: set) -> dict:
        """
        Function to traverse component types and return their parts (metadata, inputs and outputs)
        
        :param part: list with the indicated part of the component types, ``list[str]``
        :param tn_components_types: set with the components that make up the descriptor, ``set``
        :return components_data: the specified part of the component types, ``dict``
        :raise CustomSixGLibraryException:
        """
        components_data = {}
        for component in tn_components_types:
            component_path = os.path.join(self.github_6g_library_local_directory, component)
            if not os.path.isdir(component_path):
                raise CustomSixGLibraryException(f"Folder of the component '{component}' is not created in commit '{self.github_6g_library_commit_id}' of 6G-Library", 404)
            public_file = os.path.join(self.github_6g_library_local_directory, component, ".tnlcm", "public.yaml")
            if not os.path.exists(public_file):
                raise CustomSixGLibraryException(f"File '{public_file}' not found", 404)
            
            public_data = load_yaml(file_path=public_file, mode="rt", encoding="utf-8")
            
            part_data = {}
            for part in parts:
                if public_data and part in public_data:
                    part_data[component] = public_data[part]
                    if part not in components_data:
                        components_data[part] = {}
                    if part_data:
                        components_data[part].update(part_data)

        return components_data