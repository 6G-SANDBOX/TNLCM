import os
import stat

from shutil import rmtree
from git import Repo
from git.exc import GitError, GitCommandError, InvalidGitRepositoryError

repository_directory = os.path.join(os.getcwd(), "src", "repository")

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

class RepositoryHandler:

    def __init__(self, git_url=None, git_branch=None, git_commit_id=None, repository_name=None):
        if not git_url or not repository_name:
            raise GitError("Add the value of the variables git_url and repository_name")
        if not git_branch and not git_commit_id:
            raise GitError("Add the value of the variables git_branch or git_commit_id")
        if git_branch and git_commit_id:
            raise GitError("Only one field is required. Either git_branch or git_commit_id")
        self.git_url = git_url
        self.git_branch = git_branch
        self.git_commit_id = git_commit_id
        self.local_directory = os.path.join(repository_directory, repository_name)
        self.repo = None
        if os.path.exists(self.local_directory):
            self.repo = Repo(self.local_directory)
            last_clone_type = self.last_git_clone()

            if (last_clone_type == "commit" and self.git_branch) or \
                    (last_clone_type == "commit" and self.git_commit_id and not self.is_current_commit_id()) or \
                    (last_clone_type == "branch" and self.git_commit_id) or \
                    (last_clone_type == "branch" and self.git_branch and not self.is_current_branch()):
                rmtree(self.local_directory, onerror=remove_readonly)
                self.repo = None
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
    
    def git_clone_repository(self):
        try:
            if self.repo is None:
                self.repo = Repo.clone_from(self.git_url, self.local_directory)
            else:
                raise GitError("6G-Library is already cloned")
        except InvalidGitRepositoryError as e:
            raise InvalidGitRepositoryError(e)
        except GitCommandError as e:
            raise GitCommandError(e)

    def git_checkout_repository(self):
        if self.repo is not None:
            try:
                if self.git_branch:
                    self.repo.git.checkout(self.git_branch)
                else:
                    self.repo.git.checkout(self.git_commit_id)
            except InvalidGitRepositoryError as e:
                raise InvalidGitRepositoryError(e)
            except GitCommandError as e:
                raise GitCommandError(e)
        else:
            raise GitCommandError("Clone repository first")