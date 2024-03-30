import os
import re

from git import Repo
from src.exceptions.exceptions_handler import VariablesNotDefinedInEnvError, GitCloneError, GitCheckoutError
from git.exc import InvalidGitRepositoryError, GitCommandError

REPOSITORY_DIRECTORY = os.path.join(os.getcwd(), "src", "repository")

class RepositoryHandler:

    def __init__(self, git_url=None, git_branch=None, git_commit_id=None, repository_name=None):
        """Constructor"""
        if not git_url or not repository_name:
            raise VariablesNotDefinedInEnvError("Add the value of the variables git_url and repository_name", 500)
        if not git_branch and not git_commit_id:
            raise VariablesNotDefinedInEnvError("Add the value of the variables git_branch or git_commit_id", 500)
        if git_branch and git_commit_id:
            raise VariablesNotDefinedInEnvError("Only one field is required. Either git_branch or git_commit_id", 500)
        if self.is_github_repo(git_url):
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
                    output = ""
                    self.repo = Repo(self.local_directory)
                    if self.git_checkout_repository():
                        output += "updated"
                    else:
                        output += "exists"
                    if self.pull_if_necessary():
                        output += "pull"
                    return output
                except InvalidGitRepositoryError:
                    raise GitCloneError(f"The '{self.local_directory}' directory is not a GitHub repository", 500)
            else:
                self.clone_repository()
                self.git_checkout_repository()
                return "cloned"
        else:
            os.makedirs(self.local_directory)
            self.clone_repository()
            self.git_checkout_repository()
            return "cloned"
    
    def clone_repository(self):
        """Clone repository"""
        try:
            self.repo = Repo.clone_from(self.git_url, self.local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.git_url}' url is not a GitHub repository", 500)

    def git_checkout_repository(self):
        """Checkout to branch or commit_id"""
        if self.repo is not None:
            last_clone_type = self.last_git_clone()
            if (last_clone_type == "commit" and self.git_branch) or \
                    (last_clone_type == "commit" and self.git_commit_id and not self.is_current_commit_id()) or \
                    (last_clone_type == "branch" and self.git_commit_id) or \
                    (last_clone_type == "branch" and self.git_branch and not self.is_current_branch()):
                if self.git_branch:
                    try:
                        self.repo.git.checkout(self.git_branch)
                    except GitCommandError:
                        raise GitCheckoutError(f"Branch '{self.git_branch}' not in '{self.git_repository_name}' repository", 404)
                else:
                    try:
                        self.repo.git.checkout(self.git_commit_id)
                    except GitCommandError:
                        raise GitCheckoutError(f"The commit with id '{self.git_commit_id}' not in '{self.git_repository_name}' repository", 404)
                return True
            return False
        else:
            raise GitCloneError(f"Clone '{self.git_repository_name}' repository first")

    def last_git_clone(self):
        """Check if the current repository is of a commit_id or of a branch"""
        if self.repo.head.is_detached:
            return "commit"
        else:
            return "branch"
        
    def is_github_repo(self, url):
        """Check if the repository url is a git repository"""
        github_url_patterns = [
            r'^https://github.com/.+/.+\.git$',
            r'^git@github.com:.+/.+\.git$'
        ]
        for pattern in github_url_patterns:
            if re.match(pattern, url):
                return True
        return False

    def is_current_branch(self):
        """Return the current branch"""
        return self.repo.active_branch.name == self.git_branch

    def is_current_commit_id(self):
        """Return the current commit_id"""
        return self.repo.head.commit.hexsha == self.git_commit_id

    def pull_if_necessary(self):
        """Check if the repository has been updated and applies a git pull in case of changes"""
        if self.git_branch and not self.is_update_branch():
            self.repo.remotes.origin.pull()
            return True
        return False

    def is_update_branch(self):
        """Check if branch is updated"""
        if self.git_branch:
            remote_ref = f"refs/remotes/origin/{self.git_branch}"
            local_commit = self.repo.head.commit.hexsha
            remote_commit = self.repo.commit(remote_ref).hexsha
            return local_commit == remote_commit
        return False