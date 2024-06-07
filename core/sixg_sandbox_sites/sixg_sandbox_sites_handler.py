import os

from yaml import safe_load, YAMLError

from conf import SixGSandboxSitesSettings
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGSandboxSitesInvalidSiteError, InvalidContentFileError, CustomFileNotFoundError

SIXG_SANDBOX_SITES_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SixGSandboxSitesHandler():

    def __init__(self, reference_type=None, reference_value=None):
        """Constructor"""
        self.github_6g_sandbox_sites_https_url = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL
        self.github_6g_sandbox_sites_repository_name = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME
        self.github_6g_sandbox_sites_local_directory = os.path.join(SIXG_SANDBOX_SITES_DIRECTORY, self.github_6g_sandbox_sites_repository_name)
        self.github_6g_sandbox_sites_reference_type = reference_type
        self.github_6g_sandbox_sites_reference_value = reference_value
        if not reference_type and not reference_value:
            self.github_6g_sandbox_sites_reference_type = "branch"
            self.github_6g_sandbox_sites_reference_value = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_BRANCH
        self.deployment_site = None
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_sandbox_sites_https_url, github_repository_name=self.github_6g_sandbox_sites_repository_name, github_local_directory=self.github_6g_sandbox_sites_local_directory, github_reference_type=self.github_6g_sandbox_sites_reference_type, github_reference_value=self.github_6g_sandbox_sites_reference_value)
        self.github_6g_sandbox_sites_commit_id = self.repository_handler.github_commit_id

    def set_deployment_site(self, deployment_site):
        """Set deployment site in case of is correct site"""
        if deployment_site not in self.get_sites():
            raise SixGSandboxSitesInvalidSiteError(f"The 'site' should be one: {', '.join(self.get_sites())}", 404)
        self.deployment_site = deployment_site
    
    def get_tags(self):
        """Return tags"""
        return self.repository_handler.get_tags()

    def get_branches(self):
        """Return branches"""
        return self.repository_handler.get_branches()

    def get_site_available_components(self):
        """Return list with components available on a site"""
        values_file = os.path.join(self.github_6g_sandbox_sites_local_directory, ".sites", self.deployment_site, "values.yaml")
        if not os.path.exists(values_file):
            raise CustomFileNotFoundError(f"File '{values_file}' not found", 404)
        with open(values_file, "rt", encoding="utf8") as f:
            try:
                values_data = safe_load(f)
            except YAMLError:
                raise InvalidContentFileError(f"File '{values_file}' is not parsed correctly", 422)
        if "site_available_components" not in values_data:
            raise InvalidContentFileError(f"File '{values_file}' does not contain the 'site_available_components' key", 422)
        site_available_components = values_data["site_available_components"]
        return list(site_available_components.keys())

    def get_sites(self):
        """Return sites available to deploy trial networks"""
        return os.listdir(os.path.join(self.github_6g_sandbox_sites_local_directory, ".sites"))