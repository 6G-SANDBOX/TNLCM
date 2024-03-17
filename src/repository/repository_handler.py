import os
import stat
import re

from shutil import rmtree
from git import Repo, RemoteReference, Commit
from git.exc import GitCommandError, InvalidGitRepositoryError

repository_directory = os.path.join(os.getcwd(), "src", "repository")

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

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
        if os.path.exists(self.local_directory):
            if os.path.exists(os.path.join(self.local_directory, ".git")):
                try:
                    self.repo = Repo(self.local_directory)
                    last_clone_type = self.last_git_clone()

                    if (last_clone_type == "commit" and self.git_branch) or \
                            (last_clone_type == "commit" and self.git_commit_id and not self.is_current_commit_id()) or \
                            (last_clone_type == "branch" and self.git_commit_id) or \
                            (last_clone_type == "branch" and self.git_branch and not self.is_current_branch()):
                        rmtree(self.local_directory, onerror=remove_readonly)
                        self.repo = None
                except InvalidGitRepositoryError:
                    raise InvalidGitRepositoryError(f"The {self.local_directory} directory is not a repository. ")
        else:
            os.makedirs(self.local_directory)

    def is_current_branch(self):
        return self.repo.active_branch.name == self.git_branch

    def is_current_commit_id(self):
        return self.repo.head.commit.hexsha == self.git_commit_id

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
    
    def git_clone_repository(self):
        if self.repo is None:
            if self.is_github_repo(self.git_url):
                try:
                    self.repo = Repo.clone_from(self.git_url, self.local_directory)
                    return True
                except InvalidGitRepositoryError:
                    raise InvalidGitRepositoryError(f"Cannot clone because the '{self.git_url}' url is not a GitHub repository.")
            else:
                raise InvalidGitRepositoryError(f"Repository url specified '{self.git_url}' is not correct")
        return False

    def git_checkout_repository(self):
        if self.repo is not None:
            if self.git_branch:
                remote_branches_repository = []
                for ref in self.repo.refs:
                    if isinstance(ref, RemoteReference):
                        ref_name_split = ref.name.split('/')[-1]
                        if ref_name_split != "HEAD":
                            remote_branches_repository.append(ref_name_split)
                if self.git_branch in remote_branches_repository:
                    self.repo.git.checkout(self.git_branch)
                else:
                    raise GitCommandError(f"Branch '{self.git_branch}' not in '{self.git_repository_name}' repository")
            else:
                remote_commits_repository = []
                for commit in self.repo.iter_commits():
                    if isinstance(commit, Commit):
                        remote_commits_repository.append(commit.hexsha)
                if self.git_commit_id in remote_commits_repository:
                    self.repo.git.checkout(self.git_commit_id)
                else:
                    raise GitCommandError(f"The commit with id '{self.git_commit_id}' not in '{self.git_repository_name}' repository")
        else:
            raise GitCommandError(f"Clone '{self.git_repository_name}' repository first")