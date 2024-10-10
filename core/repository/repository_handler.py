import os

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import GitCloneError, GitCheckoutError

class RepositoryHandler:

    def __init__(
        self, 
        github_https_url: str, 
        github_repository_name: str, 
        github_local_directory: str, 
        github_reference_type: str, 
        github_reference_value: str, 
        github_token: str = None
    ) -> None:
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
        self._git_fetch_prune()
        self._git_delete_branches()
        self.git_checkout_repository()
        self._git_pull()
        self._set_commit_id()

    def git_clone_repository(self) -> bool:
        """
        Apply git clone

        :return: True if the repository has been cloned or cleaned successfully. Otherwise False, ``bool``
        :raise GitCloneError: if the specified directory is not a valid Git repository (error code 500)
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

    def _git_clone(self) -> None:
        """
        Clone repository

        :raise GitCloneError: if the specified directory is not a valid Git repository (error code 500)
        """
        try:
            log_handler.info(f"Clone '{self.github_repository_name}' repository into '{self.github_local_directory}'")
            self.repo = Repo.clone_from(self.github_https_url, self.github_local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.github_https_url}' url is not a GitHub repository", 500)

    def git_checkout_repository(self, default_branch: str = None) -> None:
        """
        Checkout to commit or default branch

        :param default_branch: default repository branch, ``str``
        :raise GitCheckoutError: if git checkout cannot apply (error code 404)
        """
        try:
            if not default_branch:
                log_handler.info(f"Apply checkout to '{self.github_reference_type}' '{self.github_reference_value}' of '{self.github_repository_name}' repository")
                self.repo.git.checkout(self.github_reference_value, "--")
            else:
                log_handler.info(f"Apply checkout to '{default_branch}' branch of '{self.github_repository_name}' repository")
                self.repo.git.checkout(default_branch, "--")
        except GitCommandError:
            raise GitCheckoutError(f"Reference '{self.github_reference_type}' with value '{self.github_reference_value}' is not in '{self.github_repository_name}' repository", 404)

    def _git_pull(self, default_branch: str = None) -> None:
        """
        Check if the repository has been updated and applies a git pull in case of changes

        :param default_branch: default repository branch, ``str``
        """
        if not default_branch:
            if self.github_reference_type == "branch":
                log_handler.info(f"Pull is executed in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
                self.repo.remotes.origin.pull(rebase=True)
        else:
            log_handler.info(f"Pull is executed in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
            self.repo.remotes.origin.pull()

    def _get_default_branch(self) -> str:
        """
        Function to get the default branch of the repository

        :return: the default repository branch, ``str``
        """
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

    def _set_commit_id(self) -> None:
        """
        Set last commit id associated to branch or tag
        """
        self.github_commit_id = self.repo.head.commit.hexsha
        log_handler.info(f"The latest commit of the '{self.github_reference_value}' '{self.github_reference_type}' is '{self.github_commit_id}'")

    def _git_fetch_prune(self):
        """
        Apply git fetch --prune to repository
        """
        log_handler.info(f"Apply git fetch --prune in '{self.github_repository_name}' repository located in '{self.github_local_directory}' folder")
        self.repo.remotes.origin.fetch(prune=True)
    
    def _git_delete_branches(self):
        """
        Delete branches after git fetch --prune
        """
        log_handler.info(f"Delete local branches that no longer have a remote counterpart in '{self.github_repository_name}' repository")
        local_branches = [branch.name for branch in self.repo.branches]
        remote_branches = [ref.remote_head for ref in self.repo.remotes.origin.refs if ref.remote_head != "HEAD"]
        for branch in local_branches:
            if branch not in remote_branches:
                log_handler.info(f"Deleting local branch '{branch}' as it no longer exists on the remote")
                self.repo.git.branch('-D', branch)

    def get_tags(self) -> list[str]:
        """
        Function to get repository tags

        :return: list with all tags in the repository, ``list[str]``
        :raise GitCloneError: if repository not cloned (error code 500)
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
        return [ref.remote_head for ref in self.repo.remotes.origin.refs if ref.remote_head != "HEAD"]