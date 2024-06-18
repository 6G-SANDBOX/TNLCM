import os

from yaml import safe_load, YAMLError

from conf import SixGLibrarySettings
from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGLibraryComponentsNotFoundError, InvalidContentFileError, CustomFileNotFoundError

SIXG_LIBRARY_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SixGLibraryHandler:

    def __init__(self, reference_type=None, reference_value=None):
        """
        Constructor
        
        :param reference_type: type of reference (branch, tag, commit) to checkout, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to checkout, ``str``
        """
        self.github_6g_library_https_url = SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL
        self.github_6g_library_repository_name = SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME
        self.github_6g_library_local_directory = os.path.join(SIXG_LIBRARY_DIRECTORY, self.github_6g_library_repository_name)
        self.github_6g_library_reference_type = reference_type
        self.github_6g_library_reference_value = reference_value
        if not reference_type and not reference_value:
            self.github_6g_library_reference_type = "branch"
            self.github_6g_library_reference_value = SixGLibrarySettings.GITHUB_6G_LIBRARY_BRANCH
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_library_https_url, github_repository_name=self.github_6g_library_repository_name, github_local_directory=self.github_6g_library_local_directory, github_reference_type=self.github_6g_library_reference_type, github_reference_value=self.github_6g_library_reference_value)
        self.github_6g_library_commit_id = self.repository_handler.github_commit_id

    def get_tags(self):
        """
        Return tags
        """
        return self.repository_handler.get_tags()

    def get_branches(self):
        """
        Return branches
        """
        return self.repository_handler.get_branches()
    
    def get_parts_components(self, site, list_site_available_components):
        """
        Return the metadata, inputs and outputs of the components of a specific site
        
        :param site: specific site for which components data is to be retrieved, ``str``
        :param list_site_available_components: list of components available on a site, ``list[str]``
        """
        log_handler.info(f"Get metadata, input and output part of components of a '{site}' site from the 6G-Library")
        components_data = {}
        for component in list_site_available_components:
            if not os.path.isdir(os.path.join(self.github_6g_library_local_directory, component)):
                raise SixGLibraryComponentsNotFoundError(f"No components in commit '{self.github_6g_library_commit_id}' of 6G-Library", 404) 
            if os.path.isdir(os.path.join(self.github_6g_library_local_directory, component)):
                public_file = os.path.join(self.github_6g_library_local_directory, component, ".tnlcm", "public.yaml")
                if not os.path.exists(public_file):
                    raise CustomFileNotFoundError(f"File '{public_file}' not found", 404)
                with open(public_file, "rt", encoding="utf8") as f:
                    try:
                        public_data = safe_load(f)
                    except YAMLError:
                        raise InvalidContentFileError(f"File '{public_file}' is not parsed correctly", 422)
                metadata_part = {}
                input_part = {}
                output_part = {}
                if not public_data:
                    raise InvalidContentFileError(f"File '{public_file}' is empty", 422)
                if "metadata" in public_data and public_data["metadata"]:
                    metadata_part = public_data["metadata"]
                if "input" in public_data and public_data["input"]:
                    input_part = public_data["input"]
                if "output" in public_data and public_data["output"]:
                    output_part = public_data["output"]
                components_data[component] = {
                    "metadata": metadata_part,
                    "input": input_part,
                    "output": output_part
                }
        return components_data