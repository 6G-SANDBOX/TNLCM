import os
import re

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

repository_directory = os.path.join(os.getcwd(), "src", "repository")

class RepositoryHandler:

    def __init__(self, git_url=None, git_branch=None, git_commit_id=None, repository_name=None):
        if not git_url or not repository_name:
            raise ValueError("Add the value of the variables git_url and repository_name")
        if not git_branch and not git_commit_id:
            raise ValueError("Add the value of the variables git_branch or git_commit_id")
        if git_branch and git_commit_id:
            raise ValueError("Only one field is required. Either git_branch or git_commit_id")
        self.git_url = git_url
        self.git_branch = git_branch
        self.git_commit_id = git_commit_id
        self.git_repository_name = repository_name
        self.local_directory = os.path.join(repository_directory, self.git_repository_name)
        self.repo = None

    def git_clone_repository(self):
        if os.path.exists(self.local_directory):
            if os.path.exists(os.path.join(self.local_directory, ".git")):
                try:
                    output = ""
                    self.repo = Repo(self.local_directory)
                    last_clone_type = self.last_git_clone()
                    if self.check_and_checkout_repository(last_clone_type):
                        output += "updated"
                    else:
                        output += "exists"
                    if self.pull_if_necessary():
                        output += "pull"
                    return output
                except InvalidGitRepositoryError:
                    raise InvalidGitRepositoryError(f"The {self.local_directory} directory is not a GitHub repository")
            else:
                self.clone_repository()
                self.git_checkout_repository()
                return "cloned"
        else:
            self.create_and_clone_repository()
            self.git_checkout_repository()
            return "cloned"

    def last_git_clone(self):
        if self.repo.head.is_detached:
            return "commit"
        else:
            return "branch"
        
    def is_github_repo(self, url):
        github_url_patterns = [
            r'^https://github.com/.+/.+\.git$',
            r'^git@github.com:.+/.+\.git$'
        ]
        
        for pattern in github_url_patterns:
            if re.match(pattern, url):
                return True
        return False

    def check_and_checkout_repository(self, last_clone_type):
        if (last_clone_type == "commit" and self.git_branch) or \
                (last_clone_type == "commit" and self.git_commit_id and not self.is_current_commit_id()) or \
                (last_clone_type == "branch" and self.git_commit_id) or \
                (last_clone_type == "branch" and self.git_branch and not self.is_current_branch()):
            self.git_checkout_repository()
            return True
        return False
    
    def is_current_branch(self):
        return self.repo.active_branch.name == self.git_branch

    def is_current_commit_id(self):
        return self.repo.head.commit.hexsha == self.git_commit_id

    def pull_if_necessary(self):
        if self.git_branch and not self.is_update_branch():
            self.repo.remotes.origin.pull()
            return True
        return False

    def clone_repository(self):
        if self.is_github_repo(self.git_url):
            try:
                self.repo = Repo.clone_from(self.git_url, self.local_directory)
            except InvalidGitRepositoryError:
                raise InvalidGitRepositoryError(f"Cannot clone because the '{self.git_url}' url is not a GitHub repository")
        else:
            raise InvalidGitRepositoryError(f"Repository url specified '{self.git_url}' is not correct")

    def create_and_clone_repository(self):
        os.makedirs(self.local_directory)
        self.clone_repository()

    def is_update_branch(self):
        if self.git_branch:
            remote_ref = f"refs/remotes/origin/{self.git_branch}"
            local_commit = self.repo.head.commit.hexsha
            remote_commit = self.repo.commit(remote_ref).hexsha

            return local_commit == remote_commit
        return False

    def git_checkout_repository(self):
        if self.repo is not None:
            if self.git_branch:
                try:
                    self.repo.git.checkout(self.git_branch)
                except GitCommandError:
                    raise GitCommandError(f"Branch '{self.git_branch}' not in '{self.git_repository_name}' repository")
            else:
                try:
                    self.repo.git.checkout(self.git_commit_id)
                except GitCommandError:
                    raise GitCommandError(f"The commit with id '{self.git_commit_id}' not in '{self.git_repository_name}' repository")
        else:
            raise GitCommandError(f"Clone '{self.git_repository_name}' repository first")