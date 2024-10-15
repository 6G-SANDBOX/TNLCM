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

    def git_clone(self) -> None:
        """
        Apply git clone

        :raise GitCloneError: if the specified directory is not a valid Git repository (error code 500)
        """
        try:
            if not os.path.exists(self.github_local_directory) or not os.path.exists(os.path.join(self.github_local_directory, ".git")):
                log_handler.info(f"Clone '{self.github_repository_name}' repository into '{self.github_local_directory}'")
                self.repo = Repo.clone_from(self.github_https_url, self.github_local_directory)
            else:
                self.repo = Repo(self.github_local_directory)
        except InvalidGitRepositoryError:
            raise GitCloneError(f"Cannot clone because the '{self.github_https_url}' url is not a GitHub repository", 500)

    def git_checkout(self) -> None:
        """
        Apply git checkout

        :raise GitCheckoutError: if git checkout cannot apply (error code 404)
        """
        try:
            if not self.repo:
                raise GitCheckoutError(f"Clone repository '{self.github_repository_name}' first", 404)
            log_handler.info(f"Apply checkout to '{self.github_reference_type}' '{self.github_reference_value}' of '{self.github_repository_name}' repository")
            self.repo.git.checkout(self.github_reference_value, "--")
            if self.github_reference_type != "commit":
                self.github_commit_id = self.repo.head.commit.hexsha
                self.repo.git.checkout(self.github_commit_id, "--")
            else:
                self.github_commit_id = self.github_reference_value
        except GitCommandError:
            raise GitCheckoutError(f"Reference '{self.github_reference_type}' with value '{self.github_reference_value}' is not in '{self.github_repository_name}' repository", 404)

    def get_tags(self) -> list[str]:
        """
        Function to get repository tags

        :return: list with all tags in the repository, ``list[str]``
        :raise GitCloneError: if repository not cloned (error code 500)
        """
        if not self.repo:
            raise GitCloneError(f"Clone repository '{self.github_repository_name}' first", 404)
        return [tag.name for tag in self.repo.tags]

    def get_branches(self):
        """
        Return repository branches
        """
        if not self.repo:
            raise GitCloneError(f"Clone repository '{self.github_repository_name}' first", 500)
        return [ref.remote_head for ref in self.repo.remotes.origin.refs if ref.remote_head != "HEAD"]