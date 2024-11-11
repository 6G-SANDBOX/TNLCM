import re

class RepositorySettings:
    """
    Respository Settings
    """

    @staticmethod
    def is_github_repo(url: str) -> bool:
        """
        Check if the repository url is a git repository

        :param url: url to be checked, ``str``
        :return: True if the URL is a valid GitHub repository. Otherwise False, ``bool``
        """
        github_url_patterns = [
            r"^https://github.com/.+/.+\.git$",
            r"^git@github.com:.+/.+\.git$"
        ]
        return any(re.match(pattern, url) for pattern in github_url_patterns)