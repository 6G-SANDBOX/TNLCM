import os

from conf import SixGSandboxSitesSettings
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGSandboxSitesInvalidSiteError

SIXG_SANDBOX_SITES_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SixGSandboxSitesHandler():

    def __init__(self, reference=None):
        """Constructor"""
        self.github_6g_sandbox_sites_https_url = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL
        self.github_6g_sandbox_sites_repository_name = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME
        self.github_6g_sandbox_sites_local_directory = os.path.join(SIXG_SANDBOX_SITES_DIRECTORY, self.github_6g_sandbox_sites_repository_name)
        self.github_6g_sandbox_sites_reference = reference
        if not reference:
            self.github_6g_sandbox_sites_reference = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_BRANCH
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_sandbox_sites_https_url, github_repository_name=self.github_6g_sandbox_sites_repository_name, github_local_directory=self.github_6g_sandbox_sites_local_directory, github_reference=self.github_6g_sandbox_sites_reference)
        self.repository_handler.git_clone_repository()

    def set_deployment_site(self, deployment_site):
        """Set deployment site in case of is correct site"""
        if deployment_site not in self.get_sites():
            raise SixGSandboxSitesInvalidSiteError(f"The 'site' should be one: {', '.join(self.get_sites())}", 404)
        self.deployment_site = deployment_site
    
    def get_sites(self):
        """Return sites available to deploy trial networks"""
        return os.listdir(os.path.join(self.github_6g_sandbox_sites_local_directory, ".sites"))