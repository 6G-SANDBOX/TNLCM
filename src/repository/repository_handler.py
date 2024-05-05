import os
import re

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import VariablesNotDefinedInEnvError, GitCloneError, GitCheckoutError

class RepositoryHandler:

    def __init__(self, git_https_url=None, git_repository_name=None, git_branch=None, git_commit_id=None, git_local_directory=None):
        """Constructor"""
        if not git_https_url:
            raise VariablesNotDefinedInEnvError("Add the value of the variable git_https_url", 500)
        if not git_branch and not git_commit_id:
            raise VariablesNotDefinedInEnvError("Add the value of the variables git_branch or git_commit_id", 500)
        if git_branch and git_commit_id:
            raise VariablesNotDefinedInEnvError("Only one field is required. Either git_branch or git_commit_id", 500)
        if not self._is_github_repo(git_https_url):
            raise GitCloneError(f"Repository url specified '{git_https_url}' is not correct", 500)
        self.git_https_url = git_https_url
        self.git_repository_name = git_repository_name
        self.git_branch = git_branch
        self.git_commit_id = git_commit_id
        self.git_local_directory = git_local_directory
        self.repo = None

    def git_clone_repository(self):
        """Apply git clone and git checkout to branch or commit_id"""
        if os.path.exists(self.git_local_directory):
            if os.path.exists(os.path.join(self.git_local_directory, ".git")):
                try:
                    self.repo = Repo(self.git_local_directory)
                    self._git_checkout_repository()
                    self._pull_branch()
                except InvalidGitRepositoryError:
                    raise GitCloneError(f"The '{self.git_local_directory}' directory is not a GitHub repository", 500)
            else:
                self._clone_repository()
                self._git_checkout_repository()
        else:
            os.makedirs(self.git_local_directory)
            self._clone_repository()
            self._git_checkout_repository()
    
    def _clone_repository(self):
        """Clone repository"""
        try:
            log_handler.info(f"Clone '{self.git_repository_name}' repository into '{self.git_local_directory}")
            self.repo = Repo.clone_from(self.git_https_url, self.git_local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.git_https_url}' url is not a GitHub repository", 500)

    def _git_checkout_repository(self):
        """Checkout to branch or commit_id"""
        if not self.repo:
            raise GitCloneError(f"Clone '{self.git_repository_name}' repository first")
        last_clone_type = self._last_git_clone()
        if (last_clone_type == "commit" and self.git_branch) or \
            (last_clone_type == "commit" and self.git_commit_id and not self._is_current_commit_id()) or \
            (last_clone_type == "branch" and self.git_commit_id) or \
            (last_clone_type == "branch" and self.git_branch and not self._is_current_branch()):
            if self.git_branch:
                try:
                    log_handler.info(f"Apply checkout to '{self.git_branch}' branch of '{self.git_repository_name}' repository")
                    self.repo.git.checkout(self.git_branch, "--")
                except GitCommandError:
                    raise GitCheckoutError(f"Branch '{self.git_branch}' is not in '{self.git_repository_name}' repository", 404)
            else:
                try:
                    log_handler.info(f"Apply checkout to '{self.git_commit_id}' commit of '{self.git_repository_name}' repository")
                    self.repo.git.checkout(self.git_commit_id)
                except GitCommandError:
                    raise GitCheckoutError(f"Commit with id '{self.git_commit_id}' not in '{self.git_repository_name}' repository", 404)
        else:
            if self.git_branch:
                log_handler.info(f"Repository '{self.git_repository_name}' is already on the '{self.git_branch}' branch")
            else:
                log_handler.info(f"Repository '{self.git_repository_name}' is already on the '{self.git_commit_id}' commit")

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
        return self.repo.active_branch.name == self.git_branch

    def _is_current_commit_id(self):
        """Return the current commit_id"""
        return self.repo.head.commit.hexsha == self.git_commit_id

    def _pull_branch(self):
        """Check if the repository has been updated and applies a git pull in case of changes"""
        if self.git_branch:
            log_handler.info(f"Pull is executed on the '{self.git_branch}' branch in '{self.git_repository_name}' repository located in '{self.git_local_directory}' folder")
            self.repo.remotes.origin.pull()
    
    def _is_github_repo(self, url):
        """Check if the repository url is a git repository"""
        github_url_patterns = [
            r"^https://github.com/.+/.+\.git$",
            r"^git@github.com:.+/.+\.git$",
            r"^https://.+\@github\.com/(.+)/(.+)\.git$"
        ]
        for pattern in github_url_patterns:
            if re.match(pattern, url):
                return True
        return False