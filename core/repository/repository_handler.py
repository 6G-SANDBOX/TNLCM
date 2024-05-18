import os

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import GitCloneError, GitCheckoutError

class RepositoryHandler:

    def __init__(self, github_https_url=None, github_repository_name=None, github_branch=None, github_commit_id=None, github_local_directory=None):
        """Constructor"""
        self.github_https_url = github_https_url
        self.github_repository_name = github_repository_name
        self.github_branch = github_branch
        self.github_commit_id = github_commit_id
        self.github_local_directory = github_local_directory
        self.repo = None

    def git_clone_repository(self):
        """Apply git clone and git checkout to branch or commit_id"""
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
        """Checkout to branch or commit_id"""
        if not self.repo:
            raise GitCloneError(f"Clone '{self.github_repository_name}' repository first")
        last_clone_type = self._last_git_clone()
        if (last_clone_type == "commit" and self.github_branch) or \
            (last_clone_type == "commit" and self.github_commit_id and not self._is_current_commit_id()) or \
            (last_clone_type == "branch" and self.github_commit_id) or \
            (last_clone_type == "branch" and self.github_branch and not self._is_current_branch()):
            if self.github_branch:
                try:
                    log_handler.info(f"Apply checkout to '{self.github_branch}' branch of '{self.github_repository_name}' repository")
                    self.repo.git.checkout(self.github_branch, "--")
                except GitCommandError:
                    raise GitCheckoutError(f"Branch '{self.github_branch}' is not in '{self.github_repository_name}' repository", 404)
            else:
                try:
                    log_handler.info(f"Apply checkout to '{self.github_commit_id}' commit of '{self.github_repository_name}' repository")
                    self.repo.git.checkout(self.github_commit_id)
                except GitCommandError:
                    raise GitCheckoutError(f"Commit with id '{self.github_commit_id}' not in '{self.github_repository_name}' repository", 404)
        else:
            if self.github_branch:
                log_handler.info(f"Repository '{self.github_repository_name}' is already on the '{self.github_branch}' branch")
            else:
                log_handler.info(f"Repository '{self.github_repository_name}' is already on the '{self.github_commit_id}' commit")

    def _last_git_clone(self):
        """Check if the current repository is of a commit_id or of a branch"""
        if self.repo.head.is_detached:
            log_handler.info("Current repository is a commit")
            return "commit"
        else:
            log_handler.info("Current repository is a branch")
            return "branch"
    
    def _is_current_branch(self):
        """Return the current branch"""
        return self.repo.active_branch.name == self.github_branch

    def _is_current_commit_id(self):
        """Return the current commit_id"""
        return self.repo.head.commit.hexsha == self.github_commit_id

    def _pull_branch(self):
        """Check if the repository has been updated and applies a git pull in case of changes"""
        if self.github_branch:
            log_handler.info(f"Pull is executed on the '{self.github_branch}' branch in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
            self.repo.remotes.origin.pull()