import os

from git.exc import GitCommandError
from src.repository.repository_handler import RepositoryHandler

class SixGLibraryHandler:

    def __init__(self):
        try:
            self.git_6glibrary_https_url = os.getenv("GIT_6GLIBRARY_HTTPS_URL")
            self.git_6glibrary_branch = os.getenv("GIT_6GLIBRARY_BRANCH")
            self.git_6glibrary_commit_id = os.getenv("GIT_6GLIBRARY_COMMIT_ID")
            self.git_6glibrary_repository_name = os.getenv("GIT_6GLIBRARY_REPOSITORY_NAME")
            self.repository_handler = RepositoryHandler(self.git_6glibrary_https_url, self.git_6glibrary_branch, self.git_6glibrary_commit_id, self.git_6glibrary_repository_name)
        except:
            raise
    
    def git_clone_6glibrary(self):
        try:
            self.repository_handler.git_clone_repository()
            self.repository_handler.git_checkout_repository()
        except:
            raise

    def extract_components_6glibrary(self):
        if os.path.exists(self.repository_handler.local_directory):
            components = [folder for folder in os.listdir(self.repository_handler.local_directory)
                        if os.path.isdir(os.path.join(self.repository_handler.local_directory, folder))
                        and folder not in ('.git', '.global')]
            return components
        else:
            raise GitCommandError("Clone repository first")
