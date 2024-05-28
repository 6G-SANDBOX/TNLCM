import os

from yaml import safe_load, YAMLError

from core.logs.log_handler import log_handler
from conf import SixGSandboxSitesSettings
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import KeyNotFoundError, InvalidContentFileError, CustomFileNotFoundError

SIXG_SANDBOX_SITES_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SixGSandboxSitesHandler():

    def __init__(self):
        """Constructor"""
        self.github_6g_sandbox_sites_https_url = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL
        self.github_6g_sandbox_sites_repository_name = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME
        self.github_6g_sandbox_sites_branch = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_BRANCH
        self.github_6g_sandbox_sites_local_directory = os.path.join(SIXG_SANDBOX_SITES_DIRECTORY, self.github_6g_sandbox_sites_repository_name)
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_sandbox_sites_https_url, github_repository_name=self.github_6g_sandbox_sites_repository_name, github_branch=self.github_6g_sandbox_sites_branch, github_local_directory=self.github_6g_sandbox_sites_local_directory)

    def git_clone_6g_sandbox_sites(self):
        """Clone 6G-Sandbox-Sites"""
        self.repository_handler.git_clone_repository()

    def get_site_default_network_id(self, jenkins_deployment_site):
        """Return site default network id"""
        site_file = os.path.join(self.github_6g_sandbox_sites_local_directory, ".sites", jenkins_deployment_site, "values.yaml")
        log_handler.info(f"Get site 'default' network id from '{site_file}'")
        if os.path.exists(site_file):
            with open(site_file, "rt", encoding="utf-8") as f:
                try:
                    data = safe_load(f)
                except YAMLError:
                    raise InvalidContentFileError(f"File '{site_file}' is not parsed correctly", 422)
            if "site_networks_id" not in data:
                raise KeyNotFoundError(f"Key 'site_networks_id' is missing in the file located in the path '{site_file}'", 404)
            if "default" not in data["site_networks_id"]:
                raise KeyNotFoundError(f"Key 'default' is missing into 'site_networks_id' in the file located in the path '{site_file}'", 404)
            return data["site_networks_id"]["default"]
        else:
            raise CustomFileNotFoundError(f"File '{site_file}' not found", 404)

    def get_site_public_network_id(self, jenkins_deployment_site):
        """Return site public network id"""
        site_file = os.path.join(self.github_6g_sandbox_sites_local_directory, ".sites", jenkins_deployment_site, "values.yaml")
        log_handler.info(f"Get site 'public' network id from '{site_file}'")
        if os.path.exists(site_file):
            with open(site_file, "rt", encoding="utf-8") as f:
                try:
                    data = safe_load(f)
                except YAMLError:
                    raise InvalidContentFileError(f"File '{site_file}' is not parsed correctly", 422)
            if "site_networks_id" not in data:
                raise KeyNotFoundError(f"Key 'site_networks_id' is missing in the file located in the path '{site_file}'", 404)
            if "public" not in data["site_networks_id"]:
                raise KeyNotFoundError(f"Key 'public' is missing into 'site_networks_id' in the file located in the path '{site_file}'", 404)
            return data["site_networks_id"]["public"]
        else:
            raise CustomFileNotFoundError(f"File '{site_file}' not found", 404)