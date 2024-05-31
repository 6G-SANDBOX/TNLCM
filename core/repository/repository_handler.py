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
                    self._git_checkout_repository()
                    self._pull_branch()
                except InvalidGitRepositoryError:
                    raise GitCloneError(f"The '{self.github_local_directory}' directory is not a GitHub repository", 500)
            else:
                self._clone_repository()
                self._git_checkout_repository()
        else:
            os.makedirs(self.github_local_directory)
            self._clone_repository()
            self._git_checkout_repository()

    def _clone_repository(self):
        """Clone repository"""
        try:
            log_handler.info(f"Clone '{self.github_repository_name}' repository into '{self.github_local_directory}'")
            self.repo = Repo.clone_from(self.github_https_url, self.github_local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.github_https_url}' url is not a GitHub repository", 500)

    def _git_checkout_repository(self):
        """Checkout to branch, commit or tag"""
        if not self.repo:
            raise GitCloneError(f"Clone '{self.github_repository_name}' repository first", 500)
        try:
            log_handler.info(f"Apply checkout to '{self.github_reference}' reference (branch, commit or tag) of '{self.github_repository_name}' repository")
            self.repo.git.checkout(self.github_reference, "--")
        except GitCommandError:
            raise GitCheckoutError(f"Reference '{self.github_reference}' is not in '{self.github_repository_name}' repository", 404)

    def _pull_branch(self):
        """Check if the repository has been updated and applies a git pull in case of changes"""
        if self.github_reference in self.get_branches():
            log_handler.info(f"Pull is executed in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
            self.repo.remotes.origin.pull()

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