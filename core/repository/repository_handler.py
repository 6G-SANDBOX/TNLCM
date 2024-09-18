import os

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import GitCloneError, GitCheckoutError

class RepositoryHandler:

    def __init__(self, github_https_url, github_repository_name, github_local_directory, github_reference_type, github_reference_value, github_token=None):
        """
        Constructor
        
        :param github_https_url: HTTPS URL of the GitHub repository, ``str``
        :param github_repository_name: name of the GitHub repository, ``str``
        :param github_local_directory: local directory where the repository will be cloned, ``str``        
        :param github_reference_type: type of reference (branch, tag, commit) to checkout, ``str``
        :param github_reference_value: value of the reference (branch name, tag name, commit ID) to checkout, ``str``
        :param github_token: value of token in case of private repository, ``str``
        """
        self.github_https_url = github_https_url
        self.github_repository_name = github_repository_name
        self.github_local_directory = github_local_directory
        self.github_reference_type = github_reference_type
        self.github_reference_value = github_reference_value
        self.github_token = None
        if github_token:
            self.github_token = github_token
            self.github_https_url = github_https_url.replace("https://", f"https://{github_token}@")
        self.repo = None
        self.github_commit_id = None
        if not self.git_clone_repository():
            default_branch = self._get_default_branch()
            self.git_checkout_repository(default_branch=default_branch)
            self._git_pull(default_branch=default_branch)
        self.git_checkout_repository()
        self._git_pull()
        self._set_commit_id()

    def git_clone_repository(self):
        """
        Apply git clone
        """
        if os.path.exists(self.github_local_directory):
            if os.path.exists(os.path.join(self.github_local_directory, ".git")):
                try:
                    self.repo = Repo(self.github_local_directory)
                    self.repo.git.clean("-fd")
                except InvalidGitRepositoryError:
                    raise GitCloneError(f"The '{self.github_local_directory}' directory is not a GitHub repository", 500)
            else:
                self._git_clone()
                return True
        else:
            os.makedirs(self.github_local_directory)
            self._git_clone()
            return True
        return False

    def _git_clone(self):
        """
        Clone repository
        """
        try:
            log_handler.info(f"Clone '{self.github_repository_name}' repository into '{self.github_local_directory}'")
            self.repo = Repo.clone_from(self.github_https_url, self.github_local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.github_https_url}' url is not a GitHub repository", 500)

    def git_checkout_repository(self, default_branch=None):
        """Checkout to commit or default branch"""
        try:
            if not default_branch:
                log_handler.info(f"Apply checkout to '{self.github_reference_type}' '{self.github_reference_value}' of '{self.github_repository_name}' repository")
                self.repo.git.checkout(self.github_reference_value, "--")
            else:
                log_handler.info(f"Apply checkout to '{default_branch}' branch of '{self.github_repository_name}' repository")
                self.repo.git.checkout(default_branch, "--")
        except GitCommandError:
            raise GitCheckoutError(f"Reference '{self.github_reference_type}' with value '{self.github_reference_value}' is not in '{self.github_repository_name}' repository", 404)

    def _git_pull(self, default_branch=None):
        """
        Check if the repository has been updated and applies a git pull in case of changes
        """
        if not default_branch:
            if self.github_reference_type == "branch":
                log_handler.info(f"Pull is executed in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
                self.repo.remotes.origin.pull()
        else:
            log_handler.info(f"Pull is executed in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
            self.repo.remotes.origin.pull()

    def _get_default_branch(self):
        """Return the default branch of the repository"""
        git = self.repo.git
        default_branch_info = git.remote("show", self.github_https_url).split("\n")
        default_branch = ""
        for info in default_branch_info:
            if "HEAD branch" in info:
                default_branch = info.split(":")[1].strip()
                break
        if default_branch == "":
            default_branch = "master"
        return default_branch

    def _set_commit_id(self):
        """
        Set last commit id associated to branch or tag
        """
        self.github_commit_id = self.repo.head.commit.hexsha
        log_handler.info(f"The latest commit of the '{self.github_reference_value}' '{self.github_reference_type}' is '{self.github_commit_id}'")

    def get_tags(self):
        """
        Return repository tags
        """
        if not self.repo:
            raise GitCloneError(f"Clone '{self.github_repository_name}' repository first", 500)
        return [tag.name for tag in self.repo.tags]

    def get_branches(self):
        """
        Return repository branches
        """
        if not self.repo:
            raise GitCloneError(f"Clone '{self.github_repository_name}' repository first", 500)
        return [branch.name.replace("origin/", "") for branch in self.repo.remotes.origin.refs if branch.name.replace("origin/", "") != "HEAD"]