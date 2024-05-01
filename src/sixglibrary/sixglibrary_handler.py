import os

from yaml import safe_load

from src.repository.repository_handler import RepositoryHandler
from src.exceptions.exceptions_handler import SixGLibraryComponentsNotFound

SIXGLIBRARY_DIRECTORY = os.path.join(os.getcwd(), "src", "sixglibrary")

class SixGLibraryHandler:

    def __init__(self, branch=None, commit_id=None):
        """Constructor"""
        self.git_6glibrary_https_url = os.getenv("GIT_6GLIBRARY_HTTPS_URL")
        self.git_6glibrary_repository_name = os.getenv("GIT_6GLIBRARY_REPOSITORY_NAME")
        self.git_6glibrary_local_directory = os.path.join(SIXGLIBRARY_DIRECTORY, self.git_6glibrary_repository_name)
        self.git_6glibrary_branch = None
        self.git_6glibrary_commit_id = None
        if branch is None and commit_id is not None:
            self.git_6glibrary_commit_id = commit_id
        elif branch is not None and commit_id is None:
            self.git_6glibrary_branch = branch
        elif branch is None and commit_id is None:
            self.git_6glibrary_branch = os.getenv("GIT_6GLIBRARY_BRANCH")
        else:
            self.git_6glibrary_branch = branch
            self.git_6glibrary_commit_id = commit_id
        self.repository_handler = RepositoryHandler(self.git_6glibrary_https_url, self.git_6glibrary_branch, self.git_6glibrary_commit_id, self.git_6glibrary_repository_name, self.git_6glibrary_local_directory)

    def git_clone_6glibrary(self):
        """Clone 6G-Library"""
        self.repository_handler.git_clone_repository()

    def extract_input_part_component_6glibrary(self, components):
        """The input part of the components is extracted directly from the 6G-Library"""
        input_part = {}

        for component in components:
            description_file = os.path.join(self.git_6glibrary_local_directory, component, "variables", "public.yaml")
            
            if os.path.exists(description_file):
                with open(description_file, "rt", encoding="utf8") as f:
                    description_data = safe_load(f)
                    if description_data["input"]:
                        input_part[component] = description_data["input"]
                    else:
                        input_part[component] = {}
        return input_part
    
    def extract_private_part_component_6glibrary(self, components):
        """The private part of the components is extracted directly from the 6G-Library"""
        private_part = {}

        for component in components:
            description_file = os.path.join(self.git_6glibrary_local_directory, component, "variables", "private.yaml")
            
            if os.path.exists(description_file):
                with open(description_file, "rt", encoding="utf8") as f:
                    description_data = safe_load(f)
                    if description_data:
                        private_part[component] = description_data
                    else:
                        private_part[component] = {}
        return private_part

    def extract_metadata_part_component_6glibrary(self, components):
        """The metadata part of the components is extracted directly from the 6G-Library"""
        metadata_part = {}

        for component in components:
            description_file = os.path.join(self.git_6glibrary_local_directory, component, "variables", "public.yaml")

            if os.path.exists(description_file):
                with open(description_file, "rt", encoding="utf8") as f:
                    description_data = safe_load(f)
                    if description_data["metadata"]:
                        metadata_part[component] = description_data["metadata"]
                    else:
                        metadata_part[component] = []
        return metadata_part

    def extract_parts_components_6glibrary(self):
        """Extracts input, private, and needs parts of the components from the 6G-Library"""
        components = None
        if os.path.exists(self.git_6glibrary_local_directory) and os.path.exists(os.path.join(self.git_6glibrary_local_directory, ".git")):
            components = [folder for folder in os.listdir(self.git_6glibrary_local_directory)
                          if os.path.isdir(os.path.join(self.git_6glibrary_local_directory, folder))
                          and folder not in (".git", ".global", ".vscode", "dummy-component", "suggested_skel", "skel")]
        if not components:
            if self.git_6glibrary_branch:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_branch}' branch of 6G-Library", 404)
            else:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_commit_id}' commit of 6G-Library", 404)
        else:
            input_part = self.extract_input_part_component_6glibrary(components)
            # private_part = self.extract_private_part_component_6glibrary(components)
            metadata_part = self.extract_metadata_part_component_6glibrary(components)

            component_data = {}
            for component in components:
                component_data[component] = {
                    "input": input_part[component],
                    # "private": private_part[component],
                    "metadata": metadata_part[component]
                }
            return component_data

    def extract_components_6glibrary(self):
        """6G-Library components are extracted"""
        components = None
        if os.path.exists(self.git_6glibrary_local_directory) and os.path.exists(os.path.join(self.git_6glibrary_local_directory, ".git")):
            components = [folder for folder in os.listdir(self.git_6glibrary_local_directory)
                        if os.path.isdir(os.path.join(self.git_6glibrary_local_directory, folder))
                        and folder not in (".git", ".global", ".vscode")]
        if not components:
            if self.git_6glibrary_branch:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_branch}' branch of 6G-Library", 404)
            else:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_commit_id}' commit of 6G-Library", 404)
        else:
            return components