from typing import List

from core.exceptions.exceptions import GitError
from core.utils.cli import run_command
from core.utils.os import exist_directory, join_path, remove_directory


class Git:
    def __init__(
        self,
        github_https_url: str,
        github_repository_name: str,
        github_local_directory: str,
        github_reference_type: str,
        github_reference_value: str,
        github_token: str = None,
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
            self.github_https_url = github_https_url.replace(
                old="https://", new=f"https://{github_token}@"
            )

    def add(self) -> None:
        """
        Add files to the staging area

        :param options: options to add files to the staging area, ``str``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot add files to the staging area",
                status_code=404,
            )
        run_command(command=f"git -C {self.github_local_directory} add -A")

    def branches(self) -> List[str]:
        """
        Get the list of local and remotes branches in the repository

        :return: the list of branches, ``List[str]``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot get the list of branches",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} branch -a"
        stdout, _, _ = run_command(command=command)
        branches = set()
        for line in stdout.splitlines():
            line = line.strip().replace("*", "").strip()
            if "HEAD" in line:
                continue
            if line.startswith("remotes/origin/"):
                line = line[len("remotes/origin/") :]
            branches.add(line)

        return sorted(branches)

    def checkout(self) -> None:
        """
        Checkout the specified branch, tag or commit

        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot checkout to branch, tag or commit",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} checkout {self.github_reference_value} --"
        run_command(command=command)

    def clean_fd(self) -> None:
        """
        Clean the repository

        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot clean the repository",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} clean -fd"
        run_command(command=command)

    def clone(self) -> None:
        """
        Clone a GitHub repository to the specified path
        """
        if exist_directory(path=self.github_local_directory) and not exist_directory(
            join_path(self.github_local_directory, ".git")
        ):
            remove_directory(path=self.github_local_directory)
        if not exist_directory(path=self.github_local_directory):
            command = f"git clone {self.github_https_url} {self.github_local_directory}"
            run_command(command=command)

    def commit(self, message: str) -> None:
        """
        Commit the changes to the repository

        :param message: message of the commit, ``str``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot commit the changes",
                status_code=404,
            )
        command = f'git -C {self.github_local_directory} commit -m "{message}"'
        run_command(command=command)

    def commits(self) -> List[str]:
        """
        Get the list of commits in the repository

        :return: list with all commits, ``List[str]``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot get the list of commits",
                status_code=404,
            )
        command = f'git -C {self.github_local_directory} log --pretty=format:"%H"'
        stdout, _, _ = run_command(command=command)
        return stdout.strip().split("\n") if stdout.strip() else []

    def current_branch(self) -> str:
        """
        Get the current branch of the repository

        :return: the current branch, ``str``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot get the current branch",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} branch --show-current"
        stdout, _, _ = run_command(command=command)
        return stdout.strip()

    def detect_changes(self) -> bool:
        """
        Detect changes in the repository

        :return: True if there are changes, False otherwise, ``bool``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot detect changes",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} status --porcelain"
        return bool(run_command(command=command))

    def fetch_prune(self) -> None:
        """
        Fetch the changes from the remote repository and prune the deleted branches

        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot fetch the changes and prune the deleted branches",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} fetch --prune"
        run_command(command=command)

    def get_last_commit_id(self) -> str:
        """
        Get the last commit of the repository

        :return: the last commit, ``str``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot get the last commit",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} log -1 --pretty=format:%H"
        stdout, _, _ = run_command(command=command)
        return stdout.strip()

    def pull(self) -> None:
        """
        Pull the changes from the remote repository

        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot pull the changes",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} pull"
        run_command(command=command)

    def reset_hard(self) -> None:
        """
        Reset the repository to the last commit

        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot reset the repository to the last commit",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} reset --hard"
        run_command(command=command)

    def sync_branches(self) -> None:
        """
        Sync the local and remote branches

        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot sync the branches",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} branch -vv | grep ': gone]' | awk '{{print $1}}' | xargs -r git -C {self.github_local_directory} branch -D"
        run_command(command=command)

    def tags(self) -> List[str]:
        """
        Get the list of tags in the repository

        :return: list with all tags, ``List[str]``
        :raise GitError:
        """
        if not exist_directory(path=self.github_local_directory):
            raise GitError(
                message=f"Repository {self.github_local_directory} does not exist in local. Cannot get the list of tags",
                status_code=404,
            )
        command = f"git -C {self.github_local_directory} tag --sort=-creatordate"
        stdout, _, _ = run_command(command=command)
        return stdout.strip().split("\n") if stdout.strip() else []
