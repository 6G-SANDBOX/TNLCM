import os

from yaml import safe_load, YAMLError

from conf import SixGLibrarySettings
from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGLibraryComponentsNotFound, InvalidContentFileError, CustomFileNotFoundError

SIXG_LIBRARY_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SIXG_LIBRARY_EXCLUDE_COMPONENTS = [".git", ".global", ".vscode", "dummy-component", "skel", "suggested_skel"]

class SixGLibraryHandler:

    def __init__(self, reference=None, site=None):
        """Constructor"""
        self.github_6g_library_https_url = SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL
        self.github_6g_library_repository_name = SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME
        self.github_6g_library_local_directory = os.path.join(SIXG_LIBRARY_DIRECTORY, self.github_6g_library_repository_name)
        self.github_6g_library_reference = reference
        if not reference:
            self.github_6g_library_reference = SixGLibrarySettings.GITHUB_6G_LIBRARY_BRANCH
        self.site = site
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_library_https_url, github_repository_name=self.github_6g_library_repository_name, github_local_directory=self.github_6g_library_local_directory, github_reference=self.github_6g_library_reference)
        self.repository_handler.git_clone_repository()

    def get_tags(self):
        """Return tags"""
        return self.repository_handler.get_tags()

    def get_branches(self):
        """Return branches"""
        return self.repository_handler.get_branches()
    
    def get_parts_components(self):
        """Return information about the components of a site"""
        log_handler.info(f"Get input, output and metadata part of components in '{self.site}' site from the 6G-Library")
        if not os.path.exists(self.github_6g_library_local_directory) or not os.path.exists(os.path.join(self.github_6g_library_local_directory, ".git")):
            raise SixGLibraryComponentsNotFound(f"No components in the '{self.github_6g_library_reference}' reference of 6G-Library", 404)
        else:
            components_data = {}
            for component in os.listdir(self.github_6g_library_local_directory):
                if os.path.isdir(os.path.join(self.github_6g_library_local_directory, component)) and component not in SIXG_LIBRARY_EXCLUDE_COMPONENTS:
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
                    output_part = []
                    if "metadata" in public_data:
                        metadata_part = public_data["metadata"]
                    else:
                        metadata_part = []
                    if "sites" not in public_data["metadata"]:
                        raise InvalidContentFileError(f"File '{public_file}' does not contain the 'site' key for displaying the component", 422)
                    if self.site in public_data["metadata"]["sites"]:
                        if "input" in public_data:
                            input_part = public_data["input"]
                        else:
                            input_part = {}
                        if "output" in public_data:
                            output_part = public_data["output"]
                        else:
                            output_part = []
                        components_data[component] = {
                            "metadata": metadata_part,
                            "input": input_part,
                            "output": output_part
                        }
        return components_data