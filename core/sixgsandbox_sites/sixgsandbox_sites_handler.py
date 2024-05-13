import os

from yaml import safe_load, YAMLError

from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import VariablesNotDefinedInEnvError, KeyNotFoundError, InvalidContentFileError, CustomFileNotFoundError

SIXGSANDBOX_SITES_DIRECTORY = os.path.join(os.getcwd(), "core", "sixgsandbox_sites")

class SixGSandboxSitesHandler():

    def __init__(self):
        """Constructor"""
        self.git_6gsandbox_sites_https_url = os.getenv("GIT_6GSANDBOX_SITES_HTTPS_URL")
        self.git_6gsandbox_sites_repository_name = os.getenv("GIT_6GSANDBOX_SITES_REPOSITORY_NAME")
        if not self.git_6gsandbox_sites_repository_name:
            raise VariablesNotDefinedInEnvError("Add the value of the variable 'GIT_6GSANDBOX_SITES_REPOSITORY_NAME' in the .env file", 500)
        self.git_6gsandbox_sites_branch = os.getenv("GIT_6GSANDBOX_SITES_BRANCH")
        self.git_6gsandbox_sites_local_directory = os.path.join(SIXGSANDBOX_SITES_DIRECTORY, self.git_6gsandbox_sites_repository_name)
        self.repository_handler = RepositoryHandler(git_https_url=self.git_6gsandbox_sites_https_url, git_repository_name=self.git_6gsandbox_sites_repository_name, git_branch=self.git_6gsandbox_sites_branch, git_local_directory=self.git_6gsandbox_sites_local_directory)

    def git_clone_6gsandbox_sites(self):
        """Clone 6G-Sandbox-sites"""
        self.repository_handler.git_clone_repository()

    def extract_site_default_network_id(self, jenkins_deployment_site):
        """Return the id of the site_networks_id.default"""
        site_file = os.path.join(self.git_6gsandbox_sites_local_directory, ".sites", jenkins_deployment_site, "values.yaml")
        log_handler.info(f"Extract 'site_networks_id.default' from '{site_file}'")
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

    def extract_site_public_network_id(self, jenkins_deployment_site):
        """Return the id of the site_networks_id.public"""
        site_file = os.path.join(self.git_6gsandbox_sites_local_directory, ".sites", jenkins_deployment_site, "values.yaml")
        log_handler.info(f"Extract 'site_networks_id.public' from '{site_file}'")
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