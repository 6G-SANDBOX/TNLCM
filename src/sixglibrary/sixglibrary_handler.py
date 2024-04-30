import os

from yaml import safe_load

from src.repository.repository_handler import RepositoryHandler
from src.exceptions.exceptions_handler import SixGLibraryComponentsNotFound

class SixGLibraryHandler:

    def __init__(self, branch=None, commit_id=None):
        """Constructor"""
        self.git_6glibrary_https_url = os.getenv("GIT_6GLIBRARY_HTTPS_URL")
        self.git_6glibrary_repository_name = os.getenv("GIT_6GLIBRARY_REPOSITORY_NAME")
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
        self.repository_handler = RepositoryHandler(self.git_6glibrary_https_url, self.git_6glibrary_branch, self.git_6glibrary_commit_id, self.git_6glibrary_repository_name)

    def git_clone_6glibrary(self):
        """Clone 6G-Library"""
        self.repository_handler.git_clone_repository()

    def extract_input_part_component_6glibrary(self, components):
        """The input part of the components is extracted directly from the 6G-Library"""
        input_parts = {}

        for component in components:
            description_file = os.path.join(self.repository_handler.local_directory, component, "variables", "public.yaml")
            
            if os.path.exists(description_file):
                with open(description_file, "rt", encoding="utf8") as f:
                    description_data = safe_load(f)
                    if description_data.get("input") is not None:
                        input_parts[component] = description_data.get("input", {})
                    else:
                        input_parts[component] = {}
        return input_parts
    
    def extract_private_part_component_6glibrary(self, components):
        """The private part of the components is extracted directly from the 6G-Library"""
        private_parts = {}

        for component in components:
            description_file = os.path.join(self.repository_handler.local_directory, component, "variables", "private.yaml")
            
            if os.path.exists(description_file):
                with open(description_file, "rt", encoding="utf8") as f:
                    description_data = safe_load(f)
                    if description_data is not None:
                        private_parts[component] = description_data
                    else:
                        private_parts[component] = {}
        return private_parts

    def extract_needs_part_component_6glibrary(self, components):
        """The needs part of the components is extracted directly from the 6G-Library"""
        needs_parts = {}

        for component in components:
            description_file = os.path.join(self.repository_handler.local_directory, component, "variables", "public.yaml")

            if os.path.exists(description_file):
                with open(description_file, "rt", encoding="utf8") as f:
                    description_data = safe_load(f)
                    metadata = description_data.get("metadata")
                    if metadata is not None and "needs" in metadata:
                        needs_parts[component] = metadata["needs"]
                    else:
                        needs_parts[component] = []
        return needs_parts

    def extract_info_components_6glibrary(self):
        """Extracts input, private, and needs parts of the components from the 6G-Library"""
        components = None
        if os.path.exists(self.repository_handler.local_directory) and os.path.exists(os.path.join(self.repository_handler.local_directory, ".git")):
            components = [folder for folder in os.listdir(self.repository_handler.local_directory)
                          if os.path.isdir(os.path.join(self.repository_handler.local_directory, folder))
                          and folder not in (".git", ".global", ".vscode")]
        if not components:
            if self.git_6glibrary_branch:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_branch}' branch of 6G-Library", 404)
            else:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_commit_id}' commit of 6G-Library", 404)
        else:
            input_parts = self.extract_input_part_component_6glibrary(components)
            # private_parts = self.extract_private_part_component_6glibrary(components)
            needs_parts = self.extract_needs_part_component_6glibrary(components)
            
            component_data = {}
            for component in components:
                component_data[component] = {
                    "input": input_parts.get(component, {}),
                    # "private": private_parts.get(component, {}),
                    "needs": needs_parts.get(component, [])
                }
            return component_data

    def extract_components_6glibrary(self):
        """6G-Library components are extracted"""
        components = None
        if os.path.exists(self.repository_handler.local_directory) and os.path.exists(os.path.join(self.repository_handler.local_directory, ".git")):
            components = [folder for folder in os.listdir(self.repository_handler.local_directory)
                        if os.path.isdir(os.path.join(self.repository_handler.local_directory, folder))
                        and folder not in (".git", ".global")]
        if not components:
            if self.git_6glibrary_branch:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_branch}' branch of 6G-Library", 404)
            else:
                raise SixGLibraryComponentsNotFound(f"No components in the '{self.git_6glibrary_commit_id}' commit of 6G-Library", 404)
        else:
            return components