import os
import re

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import VariablesNotDefinedInEnvError, GitCloneError, GitCheckoutError

REPOSITORY_DIRECTORY = os.path.join(os.getcwd(), "src", "repository")

class RepositoryHandler:

    def __init__(self, git_url=None, git_branch=None, git_commit_id=None, repository_name=None):
        """Constructor"""
        if git_url is None or repository_name is None:
            raise VariablesNotDefinedInEnvError("Add the value of the variables git_url and repository_name", 500)
        if git_branch is None and git_commit_id is None:
            raise VariablesNotDefinedInEnvError("Add the value of the variables git_branch or git_commit_id", 500)
        if git_branch is not None and git_commit_id is not None:
            raise VariablesNotDefinedInEnvError("Only one field is required. Either git_branch or git_commit_id", 500)
        if self._is_github_repo(git_url):
            self.git_url = git_url
        else:
            raise GitCloneError(f"Repository url specified '{self.git_url}' is not correct", 500)
        self.git_branch = git_branch
        self.git_commit_id = git_commit_id
        self.git_repository_name = repository_name
        self.local_directory = os.path.join(REPOSITORY_DIRECTORY, self.git_repository_name)
        self.repo = None

    def git_clone_repository(self):
        """Apply git clone and git checkout to branch or commit_id"""
        if os.path.exists(self.local_directory):
            if os.path.exists(os.path.join(self.local_directory, ".git")):
                try:
                    self.repo = Repo(self.local_directory)
                    self._git_checkout_repository()
                    self._pull_branch()
                except InvalidGitRepositoryError:
                    raise GitCloneError(f"The '{self.local_directory}' directory is not a GitHub repository", 500)
            else:
                self._clone_repository()
                self._git_checkout_repository()
        else:
            os.makedirs(self.local_directory)
            self._clone_repository()
            self._git_checkout_repository()
    
    def _clone_repository(self):
        """Clone repository"""
        try:
            log_handler.info(f"Clone '{self.git_repository_name}' repository")
            self.repo = Repo.clone_from(self.git_url, self.local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.git_url}' url is not a GitHub repository", 500)

    def _git_checkout_repository(self):
        """Checkout to branch or commit_id"""
        if self.repo is not None:
            last_clone_type = self._last_git_clone()
            if (last_clone_type == "commit" and self.git_branch) or \
                    (last_clone_type == "commit" and self.git_commit_id and not self._is_current_commit_id()) or \
                    (last_clone_type == "branch" and self.git_commit_id) or \
                    (last_clone_type == "branch" and self.git_branch and not self._is_current_branch()):
                if self.git_branch:
                    try:
                        log_handler.info(f"Checkout to '{self.git_branch}' branch of '{self.git_repository_name}' repository")
                        self.repo.git.checkout(self.git_branch, "--")
                    except GitCommandError:
                        log_handler.error(f"Branch '{self.git_branch}' is not in '{self.git_repository_name}' repository")
                        raise GitCheckoutError(f"Branch '{self.git_branch}' is not in '{self.git_repository_name}' repository", 404)
                else:
                    try:
                        log_handler.info(f"Checkout to '{self.git_commit_id}' commit of '{self.git_repository_name}' repository")
                        self.repo.git.checkout(self.git_commit_id)
                    except GitCommandError:
                        log_handler.error(f"Commit with id '{self.git_commit_id}' not in '{self.git_repository_name}' repository")
                        raise GitCheckoutError(f"Commit with id '{self.git_commit_id}' not in '{self.git_repository_name}' repository", 404)
        else:
            log_handler.error(f"Clone '{self.git_repository_name}' repository first")
            raise GitCloneError(f"Clone '{self.git_repository_name}' repository first")

    def _last_git_clone(self):
        """Check if the current repository is of a commit_id or of a branch"""
        if self.repo.head.is_detached:
            return "commit"
        else:
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
            log_handler.info(f"Pull execute in branch '{self.git_branch}'")
            self.repo.remotes.origin.pull()
    
    def _is_github_repo(self, url):
        """Check if the repository url is a git repository"""
        github_url_patterns = [
            r'^https://github.com/.+/.+\.git$',
            r'^git@github.com:.+/.+\.git$'
        ]
        for pattern in github_url_patterns:
            if re.match(pattern, url):
                return True
        return False