from git import Repo

from threading import Lock

from core.utils.os_handler import exists_path, join_path
from core.exceptions.exceptions_handler import CustomGitException

git_index_lock = Lock()

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
        :param github_reference_type: type of reference (branch, tag, commit) to switch, ``str``
        :param github_reference_value: value of the reference (branch name, tag name, commit ID) to switch, ``str``
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
        Git clone
        """
        if not exists_path(path=self.github_local_directory) or not exists_path(path=join_path(self.github_local_directory, ".git")):
            self.repo = Repo.clone_from(self.github_https_url, self.github_local_directory)
        else:
            self.repo = Repo(self.github_local_directory)

    def git_checkout(self) -> None:
        """
        Git checkout

        :raise CustomGitException:
        """
        with git_index_lock:
            if not self.repo:
                raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
            self.repo.git.checkout(self.github_reference_value, "--")

    def git_switch(self) -> None:
        """
        Git switch

        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        self.github_commit_id = self.repo.head.commit.hexsha
        self.repo.git.switch("--detach", self.github_commit_id)

    def git_branches(self) -> list[str]:
        """
        Git branches

        :return: list with all remote branches, ``list[str]``
        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        return [ref.remote_head for ref in self.repo.remotes.origin.refs if ref.remote_head != "HEAD"]

    def git_tags(self) -> list[str]:
        """
        Git tags

        :return: list with all tags, ``list[str]``
        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        return [tag.name for tag in self.repo.tags]
    
    def git_commits(self) -> list[str]:
        """
        Git commits

        :return: list with all commits, ``list[str]``
        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        return [commit.hexsha for commit in self.repo.iter_commits()]

    def git_pull(self) -> None:
        """
        Git pull

        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        self.repo.git.clean("-fd")
        if self.github_reference_type == "branch":
            self.repo.remotes.origin.pull()

    def git_fetch_prune(self) -> None:
        """
        Git fetch prune

        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        self.repo.remotes.origin.fetch(prune=True)

    def git_clean(self) -> None:
        """
        Git clean

        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        self.repo.git.clean("-fd")

    def git_reset(self) -> None:
        """
        Git reset

        :raise CustomGitException:
        """
        if not self.repo:
            raise CustomGitException(f"Clone repository {self.github_repository_name} first", 404)
        self.repo.head.reset(index=True, working_tree=True)
