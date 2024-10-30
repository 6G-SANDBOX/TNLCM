import os

from yaml import safe_load
from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.constants import DEFAULT_VAULT_ID_MATCH

from conf import SixGSandboxSitesSettings
from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.utils.file_handler import load_yaml, load_file, save_yaml
from core.exceptions.exceptions_handler import CustomSixGSandboxSitesException

class SixGSandboxSitesHandler():

    def __init__(
        self, 
        reference_type: str = None, 
        reference_value: str = None,
        directory_path: str = None
    ) -> None:
        """
        Constructor
        
        :param reference_type: type of reference (branch, tag, commit) to switch, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to switch, ``str``
        :param directory_path: directory path into which the 6G-Sandbox-Sites is to be cloned, ``str``
        """
        self.github_6g_sandbox_sites_https_url = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL
        self.github_6g_sandbox_sites_repository_name = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME
        self.github_6g_sandbox_sites_local_directory = os.path.join(directory_path, self.github_6g_sandbox_sites_repository_name)
        self.github_6g_sandbox_sites_reference_type = reference_type
        self.github_6g_sandbox_sites_reference_value = reference_value
        if reference_type == "branch" and reference_value:
            self.github_6g_sandbox_sites_reference_value = reference_value
        elif reference_type == "commit" and reference_value:
            self.github_6g_sandbox_sites_reference_value = reference_value
        elif reference_type == "tag" and reference_value:
            self.github_6g_sandbox_sites_reference_value = f"refs/tags/{reference_value}"
        else:
            self.github_6g_sandbox_sites_reference_type = "branch"
            self.github_6g_sandbox_sites_reference_value = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_BRANCH
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_sandbox_sites_https_url, github_repository_name=self.github_6g_sandbox_sites_repository_name, github_local_directory=self.github_6g_sandbox_sites_local_directory, github_reference_type=self.github_6g_sandbox_sites_reference_type, github_reference_value=self.github_6g_sandbox_sites_reference_value)
        self.github_6g_sandbox_sites_commit_id = None

    def validate_site(self, deployment_site: str) -> None:
        """
        Check if deployment site is valid for deploy trial network
        
        :param deployment_site: trial network deployment site, ``str``
        :raise CustomSixGSandboxSitesException:
        """
        if deployment_site not in self.get_sites():
            raise CustomSixGSandboxSitesException(f"The 'site' should be one: {', '.join(self.get_sites())}", 404)

        password = SixGSandboxSitesSettings.SITES_TOKEN
        secret = password.encode("utf-8")
        vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
        core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, deployment_site, "core.yaml")
        encrypted_data = load_file(file_path=core_file, mode="rb", encoding=None)
        decrypted_data = vault.decrypt(encrypted_data)
        decrypted_yaml = safe_load(decrypted_data)
        save_yaml(data=decrypted_yaml, file_path=os.path.join(self.github_6g_sandbox_sites_local_directory, deployment_site, "core_decrypt.yaml"))
    
    def git_clone(self) -> None:
        """
        Git clone
        """
        self.repository_handler.git_clone()
    
    def git_checkout(self) -> None:
        """
        Git checkout
        """
        self.repository_handler.git_checkout()

    def git_switch(self) -> None:
        """
        Git switch
        """
        self.repository_handler.git_switch()
        self.github_6g_sandbox_sites_commit_id = self.repository_handler.github_commit_id

    def git_branches(self) -> list[str]:
        """
        Git branches

        :return: list with 6G-Sandbox-Sites branches, ``list[str]``
        """
        return self.repository_handler.git_branches()

    def git_tags(self) -> list[str]:
        """
        Git tags

        :return: list with 6G-Sandbox-Sites tags, ``list[str]``
        """
        return self.repository_handler.git_tags()

    def get_site_available_components(self, deployment_site: str) -> dict:
        """
        Function to get all information of all components available on a site

        :param deployment_site: trial network deployment site, ``str``
        :return: dictionary with all information of all components available on a site, ``dict``
        :raise CustomSixGSandboxSitesException:
        """
        decrypted_core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, deployment_site, "core_decrypt.yaml")
        if not os.path.exists(decrypted_core_file):
            raise CustomSixGSandboxSitesException(f"File '{decrypted_core_file}' not found", 404)
        data = load_yaml(file_path=decrypted_core_file, mode="rt", encoding="utf-8")
        if not data or "site_available_components" not in data:
            return {}
        site_available_components = data["site_available_components"]
        return site_available_components

    def get_sites(self) -> list[str]:
        """
        Function to get sites available to deploy trial networks

        :return: list with deployment sites available for deploy trial networks
        """
        return [site for site in os.listdir(self.github_6g_sandbox_sites_local_directory) if not site.startswith(".") and os.path.isdir(os.path.join(self.github_6g_sandbox_sites_local_directory, site))]
    
    def validate_components_site(self, tn_id: str, deployment_site: str, tn_components_types: set) -> None:
        """
        Function to check if components in the descriptor are in the site

        :param tn_id: trial network identifier, ``str``
        :param deployment_site: trial network deployment site, ``str``
        :param tn_components_types: set with the components that make up the descriptor, ``set``
        :raise CustomSixGSandboxSitesException:
        """
        site_available_components = self.get_site_available_components(deployment_site)
        list_site_available_components = list(site_available_components.keys())
        for component in tn_components_types:
            if component not in list_site_available_components:
                raise CustomSixGSandboxSitesException(f"Component '{component}' entered in descriptor file not found in '{deployment_site}' site", 404)
            log_handler.info(f"[{tn_id}] - Component type '{component}' is on '{deployment_site}' site")