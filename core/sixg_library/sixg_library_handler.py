import os

from yaml import safe_load, YAMLError

from conf import SixGLibrarySettings
from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGLibraryComponentFolderNotFoundError, InvalidContentFileError, CustomFileNotFoundError

class SixGLibraryHandler:

    def __init__(
        self, 
        reference_type: str = None, 
        reference_value: str = None,
        tn_folder: str = None
    ) -> None:
        """
        Constructor
        
        :param reference_type: type of reference (branch, tag, commit) to checkout, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to checkout, ``str``
        :param tn_folder: folder into which the 6G-Library is to be cloned, ``str``
        """
        self.github_6g_library_https_url = SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL
        self.github_6g_library_repository_name = SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME
        self.github_6g_library_local_directory = os.path.join(tn_folder, self.github_6g_library_repository_name)
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
        Apply git clone repository
        """
        self.repository_handler.git_clone()
    
    def git_checkout(self) -> None:
        """
        Apply git checkout repository
        """
        self.repository_handler.git_checkout()
        self.github_6g_library_commit_id = self.repository_handler.github_commit_id

    def get_tags(self) -> list[str]:
        """
        Return tags

        :return: list with 6G-Library tags, ``list[str]``
        """
        return self.repository_handler.get_tags()

    def get_branches(self) -> list[str]:
        """
        Return branches

        :return: list with 6G-Library branches, ``list[str]``
        """
        return self.repository_handler.get_branches()
    
    def get_tn_components_parts(self, deployment_site: str, parts: list[str], tn_components_types: list[str]) -> dict:
        """
        Function to traverse component types and return their parts (metadata, inputs and outputs)
        
        :param deployment_site: specific deployment site for which components data is to be retrieved, ``str``
        :param part: list with the indicated part of the component types, ``list[str]``
        :param tn_components_types: list of the components that make up the descriptor, ``list[str]``
        :return components_data: the specified part of the component types, ``dict``
        :raise SixGLibraryComponentFolderNotFoundError: if folder of the component not declared in repository (error code 404)
        :raise CustomFileNotFoundError: if public file not found in component folder (error code 404)
        :raise InvalidContentFileError: if the information in the file is not parsed correctly (error code 422)
        """
        log_handler.info(f"Get {', '.join(parts)} part(s) of components for a '{deployment_site}' deployment site from the 6G-Library")
        components_data = {}
        for component in tn_components_types:
            component_path = os.path.join(self.github_6g_library_local_directory, component)
            if not os.path.isdir(component_path):
                raise SixGLibraryComponentFolderNotFoundError(f"Folder of the component '{component}' is not created in commit '{self.github_6g_library_commit_id}' of 6G-Library", 404)
            public_file = os.path.join(self.github_6g_library_local_directory, component, ".tnlcm", "public.yaml")
            if not os.path.exists(public_file):
                raise CustomFileNotFoundError(f"File '{public_file}' not found", 404)
            with open(public_file, "rt", encoding="utf8") as f:
                try:
                    public_data = safe_load(f)
                except YAMLError:
                    raise InvalidContentFileError(f"File '{public_file}' is not parsed correctly", 422)
            
            part_data = {}
            for part in parts:
                if public_data and part in public_data:
                    part_data[component] = public_data[part]
                    if part not in components_data:
                        components_data[part] = {}
                    if part_data:
                        components_data[part].update(part_data)

        return components_data