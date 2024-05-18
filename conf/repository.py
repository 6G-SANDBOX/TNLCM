import re

class RepositorySettings:
    """Respository Settings"""

    @staticmethod
    def is_github_repo(url):
        """Check if the repository url is a git repository"""
        github_url_patterns = [
            r"^https://github.com/.+/.+\.git$",
            r"^git@github.com:.+/.+\.git$",
            r"^https://.+\@github\.com/(.+)/(.+)\.git$"
        ]
        for pattern in github_url_patterns:
            if re.match(pattern, url):
                return True
        return False