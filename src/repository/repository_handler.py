import os
import stat

from shutil import rmtree
from git import Repo, exc

repository_directory = os.path.join(os.getcwd(), "src", "repository")

class RepositoryHandler:

    def __init__(self, git_url):
        self.git_url = git_url
        if not os.path.exists(repository_directory):
            os.makedirs(repository_directory)

    @staticmethod
    def onerror(func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.

        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.

        If the error is for another reason it re-raises the error.
        
        Usage : ``shutil.rmtree(path, onerror=onerror)``
        """
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

    def clone_repository(self, repository_name, branch):
        try:
            local_directory = os.path.join(repository_directory, repository_name)
            if os.path.exists(local_directory):
                rmtree(local_directory, onerror=self.onerror)
            Repo.clone_from(self.git_url, local_directory, branch=branch)
        except exc.GitCommandError as e:
            print(e)

    def extract_components(self):
        pass