import os

from src.repository.repository_handler import RepositoryHandler

class SixGLibraryHandler:

    def __init__(self):
        self.git_6glibrary_https_url = os.getenv("GIT_6GLIBRARY_HTTPS_URL")
        self.git_6glibrary_branch = os.getenv("GIT_6GLIBRARY_BRANCH")
        self.git_6glibrary_commit_id = os.getenv("GIT_6GLIBRARY_COMMIT_ID")
        self.git_6glibrary_repository_name = os.getenv("GIT_6GLIBRARY_REPOSITORY_NAME")
        self.repository_handler = RepositoryHandler(self.git_6glibrary_https_url, self.git_6glibrary_branch, self.git_6glibrary_commit_id, self.git_6glibrary_repository_name)
    
    def git_clone_6glibrary(self):
        return self.repository_handler.git_clone_repository()
    
    def git_checkout_6glibrary(self):
        self.repository_handler.git_checkout_repository()

    def extract_components_6glibrary(self):
        components = None
        if os.path.exists(self.repository_handler.local_directory) and os.path.exists(os.path.join(self.repository_handler.local_directory, ".git")):
            components = [folder for folder in os.listdir(self.repository_handler.local_directory)
                        if os.path.isdir(os.path.join(self.repository_handler.local_directory, folder))
                        and folder not in (".git", ".global")]
        return components
