import os

from conf import SixGSandboxSitesSettings
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import GitRequiredFieldError, SixGSandboxSitesInvalidSiteError

SIXG_SANDBOX_SITES_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SixGSandboxSitesHandler():

    def __init__(self, branch=None, commit_id=None, tag=None):
        """Constructor"""
        self.github_6g_sandbox_sites_https_url = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL
        self.github_6g_sandbox_sites_repository_name = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME
        self.github_6g_sandbox_sites_local_directory = os.path.join(SIXG_SANDBOX_SITES_DIRECTORY, self.github_6g_sandbox_sites_repository_name)
        self.github_6g_sandbox_sites_branch = None
        self.github_6g_sandbox_sites_commit_id = None
        self.github_6g_sandbox_sites_tag = None
        self.deployment_site = None
        if branch and not commit_id and not tag:
            self.github_6g_sandbox_sites_branch = branch
        elif not branch and commit_id and not tag:
            self.github_6g_sandbox_sites_commit_id = commit_id
        elif not branch and not commit_id and tag:
            self.github_6g_sandbox_sites_tag = tag
        elif not branch and not commit_id and not tag:
            self.github_6g_sandbox_sites_branch = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_BRANCH
        else:
            raise GitRequiredFieldError("Only one field is required. Either branch, commit_id or tag", 400)
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_sandbox_sites_https_url, github_repository_name=self.github_6g_sandbox_sites_repository_name, github_branch=self.github_6g_sandbox_sites_branch, github_commit_id=self.github_6g_sandbox_sites_commit_id, github_tag=self.github_6g_sandbox_sites_tag, github_local_directory=self.github_6g_sandbox_sites_local_directory)
        self.repository_handler.git_clone_repository()

    def set_deployment_site(self, deployment_site):
        """Set deployment site in case of is correct site"""
        if deployment_site not in self.get_sites():
            raise SixGSandboxSitesInvalidSiteError(f"The 'site' should be one: {', '.join(self.get_sites())}", 404)
        self.deployment_site = deployment_site
    
    def get_sites(self):
        """Return sites available to deploy trial networks"""
        return os.listdir(os.path.join(self.github_6g_sandbox_sites_local_directory, ".sites"))