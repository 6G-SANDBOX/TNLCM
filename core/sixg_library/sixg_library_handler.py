import os

from yaml import safe_load, YAMLError

from conf import SixGLibrarySettings
from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGLibraryComponentsNotFound, InvalidContentFileError, CustomFileNotFoundError, GitRequiredFieldError

SIXG_LIBRARY_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SIXG_LIBRARY_EXCLUDE_FOLDERS = [".git", ".global", ".vscode", "dummy-component", "skel", "suggested_skel"]

class SixGLibraryHandler:

    def __init__(self, branch=None, commit_id=None):
        """Constructor"""
        self.github_6g_library_https_url = SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL
        self.github_6g_library_repository_name = SixGLibrarySettings.GITHUB_6G_LIBRARY_REPOSITORY_NAME
        self.github_6g_library_local_directory = os.path.join(SIXG_LIBRARY_DIRECTORY, self.github_6g_library_repository_name)
        self.github_6g_library_branch = None
        self.github_6g_library_commit_id = None
        if not branch and commit_id:
            self.github_6g_library_commit_id = commit_id
        elif branch and not commit_id:
            self.github_6g_library_branch = branch
        elif not branch and not commit_id:
            self.github_6g_library_branch = SixGLibrarySettings.GITHUB_6G_LIBRARY_BRANCH
        else:
            raise GitRequiredFieldError("Only one field is required. Either git_branch or git_commit_id", 400)
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_library_https_url, github_repository_name=self.github_6g_library_repository_name, github_branch=self.github_6g_library_branch, github_commit_id=self.github_6g_library_commit_id, github_local_directory=self.github_6g_library_local_directory)

    def git_clone_6g_library(self):
        """Clone 6G-Library"""
        self.repository_handler.git_clone_repository()

    def extract_input_part_component(self, components):
        """The input part of the components is extracted directly from the 6G-Library"""
        log_handler.info("Extract input part of components from the 6G-Library")
        input_part = {}
        for component in components:
            public_file = os.path.join(self.github_6g_library_local_directory, component, ".tnlcm", "public.yaml")
            if not os.path.exists(public_file):
                raise CustomFileNotFoundError(f"File '{public_file}' not found", 404)
            with open(public_file, "rt", encoding="utf8") as f:
                try:
                    public_data = safe_load(f)
                except YAMLError:
                    raise InvalidContentFileError(f"File '{public_file}' is not parsed correctly", 422)
            if "input" in public_data:
                input_part[component] = public_data["input"]
            else:
                input_part[component] = {}
        return input_part

    def extract_metadata_part_component(self, components):
        """The metadata part of the components is extracted directly from the 6G-Library"""
        log_handler.info("Extract metadata of components from the 6G-Library")
        metadata_part = {}
        for component in components:
            public_file = os.path.join(self.github_6g_library_local_directory, component, ".tnlcm", "public.yaml")
            if not os.path.exists(public_file):
                raise CustomFileNotFoundError(f"File '{public_file}' not found", 404)
            with open(public_file, "rt", encoding="utf8") as f:
                try:
                    public_data = safe_load(f)
                except YAMLError:
                    raise InvalidContentFileError(f"File '{public_file}' is not parsed correctly", 422)
            if "metadata" in public_data:
                metadata_part[component] = public_data["metadata"]
            else:
                metadata_part[component] = []
        return metadata_part

    def extract_private_part_component(self, components):
        """The private part of the components is extracted directly from the 6G-Library"""
        log_handler.info("Extract private part of components from the 6G-Library")
        private_part = {}
        for component in components:
            private_file = os.path.join(self.github_6g_library_local_directory, component, "variables", "hypervisor", "one", "private.yaml")
            if not os.path.exists(private_file):
                raise CustomFileNotFoundError(f"File '{private_file}' not found", 404)
            with open(private_file, "rt", encoding="utf8") as f:
                try:
                    private_data = safe_load(f)
                except YAMLError:
                    raise InvalidContentFileError(f"File '{private_file}' is not parsed correctly", 422)
            if private_data:
                private_part[component] = private_data
            else:
                private_part[component] = {}
        return private_part

    def extract_output_part_component(self, components):
        """The output part of the components is extracted directly from the 6G-Library"""
        log_handler.info("Extract output part of components from the 6G-Library")
        output_part = {}
        for component in components:
            public_file = os.path.join(self.github_6g_library_local_directory, component, ".tnlcm", "public.yaml")
            if not os.path.exists(public_file):
                raise CustomFileNotFoundError(f"File '{public_file}' not found", 404)
            with open(public_file, "rt", encoding="utf8") as f:
                try:
                    public_data = safe_load(f)
                except YAMLError:
                    raise InvalidContentFileError(f"File '{public_file}' is not parsed correctly", 422)
            if "output" in public_data:
                output_part[component] = public_data["output"]
            else:
                output_part[component] = []
        return output_part

    def extract_parts_components(self):
        """Extracts input, private, and dependencies parts of the components from the 6G-Library"""
        log_handler.info("Extract parts of components from the 6G-Library")
        if not os.path.exists(self.github_6g_library_local_directory) or not os.path.exists(os.path.join(self.github_6g_library_local_directory, ".git")):
            if self.github_6g_library_branch:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.github_6g_library_branch}' branch of 6G-Library", 404)
            else:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.github_6g_library_commit_id}' commit of 6G-Library", 404)
        else:
            components = [folder for folder in os.listdir(self.github_6g_library_local_directory)
                if os.path.isdir(os.path.join(self.github_6g_library_local_directory, folder))
                and folder not in SIXG_LIBRARY_EXCLUDE_FOLDERS]

            input_part = self.extract_input_part_component(components)
            # private_part = self.extract_private_part_component(components)
            metadata_part = self.extract_metadata_part_component(components)
            output_part = self.extract_output_part_component(components)

            component_data = {}
            for component in components:
                component_data[component] = {
                    "input": input_part[component],
                    # "private": private_part[component],
                    "metadata": metadata_part[component],
                    "output": output_part[component]
                }
            return component_data

    def extract_components(self):
        """6G-Library components are extracted"""
        log_handler.info("Extract components from the 6G-Library according to the folders stored in the repository")
        if not os.path.exists(self.github_6g_library_local_directory) or not os.path.exists(os.path.join(self.github_6g_library_local_directory, ".git")):
            if self.github_6g_library_branch:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.github_6g_library_branch}' branch of 6G-Library", 404)
            else:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.github_6g_library_commit_id}' commit of 6G-Library", 404)
        else:
            return [folder for folder in os.listdir(self.github_6g_library_local_directory)
                if os.path.isdir(os.path.join(self.github_6g_library_local_directory, folder))
                and folder not in SIXG_LIBRARY_EXCLUDE_FOLDERS]