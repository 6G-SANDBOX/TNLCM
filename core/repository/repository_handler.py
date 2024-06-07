import os

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import GitCloneError, GitCheckoutError

class RepositoryHandler:

    def __init__(self, github_https_url=None, github_repository_name=None, github_local_directory=None, github_reference=None):
        """Constructor"""
        self.github_https_url = github_https_url
        self.github_repository_name = github_repository_name
        self.github_local_directory = github_local_directory
        self.github_reference = github_reference
        self.repo = None

    def git_clone_repository(self):
        """Apply git clone and git checkout to branch, commit or tag"""
        if os.path.exists(self.github_local_directory):
            if os.path.exists(os.path.join(self.github_local_directory, ".git")):
                try:
                    self.repo = Repo(self.github_local_directory)
                    self._git_checkout(reference="main")
                    self._git_pull()
                    self._git_checkout()
                except InvalidGitRepositoryError:
                    raise GitCloneError(f"The '{self.github_local_directory}' directory is not a GitHub repository", 500)
            else:
                self._git_clone()
                self._git_checkout()
        else:
            os.makedirs(self.github_local_directory)
            self._git_clone()
            self._git_checkout()

    def _git_clone(self):
        """Clone repository"""
        try:
            log_handler.info(f"Clone '{self.github_repository_name}' repository into '{self.github_local_directory}'")
            self.repo = Repo.clone_from(self.github_https_url, self.github_local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.github_https_url}' url is not a GitHub repository", 500)

    def _git_checkout(self, reference=None):
        """Checkout to branch, commit or tag"""
        if not self.repo:
            raise GitCloneError(f"Clone '{self.github_repository_name}' repository first", 500)
        try:
            if not reference:
                log_handler.info(f"Apply checkout to '{self.github_reference}' reference (branch, commit or tag) of '{self.github_repository_name}' repository")
                self.repo.git.checkout(self.github_reference, "--")
            else:
                log_handler.info(f"Apply checkout to '{reference}' reference (branch, commit or tag) of '{self.github_repository_name}' repository")
                self.repo.git.checkout(reference, "--")
        except GitCommandError:
            raise GitCheckoutError(f"Reference '{self.github_reference}' is not in '{self.github_repository_name}' repository", 404)

    def _git_pull(self):
        """Check if the repository has been updated and applies a git pull in case of changes"""
        if not self.repo.head.is_detached:
            log_handler.info(f"Pull is executed in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
            self.repo.remotes.origin.pull()

    def _get_default_branch(self):
        """Return the default branch of the repository"""
        return self.repo.remotes.origin.refs[self.repo.head.reference].name.replace("origin/", "")

    def get_tags(self):
        """Return repository tags"""
        if not self.repo:
            raise GitCloneError(f"Clone '{self.github_repository_name}' repository first", 500)
        return [tag.name for tag in self.repo.tags]

    def get_branches(self):
        """Return repository branches"""
        if not self.repo:
            raise GitCloneError(f"Clone '{self.github_repository_name}' repository first", 500)
        return [branch.name.replace("origin/", "") for branch in self.repo.remotes.origin.refs if branch.name.replace("origin/", "") != "HEAD"]