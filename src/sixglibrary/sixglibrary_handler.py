import os

from src.repository.repository_handler import RepositoryHandler
from src.exceptions.exceptions_handler import SixGLibraryComponentsNotFound

class SixGLibraryHandler:

    def __init__(self, branch=None, commit_id=None):
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
        return self.repository_handler.git_clone_repository()

    def extract_components_6glibrary(self):
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