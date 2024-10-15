import os

from yaml import safe_load, YAMLError, safe_dump
from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.errors import AnsibleError

from conf import SixGSandboxSitesSettings
from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGSandboxSitesInvalidSiteError, SixGSandboxSitesComponentsNotFoundError, InvalidContentFileError, CustomFileNotFoundError, SixGSandboxSitesDecryptError

class SixGSandboxSitesHandler():

    def __init__(
        self, 
        reference_type: str = None, 
        reference_value: str = None,
        tn_folder: str = None
    ) -> None:
        """
        Constructor
        
        :param reference_type: type of reference (branch, tag, commit) to checkout, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to checkout, ``str``
        :param tn_folder: folder into which the 6G-Sandbox-Sites is to be cloned, ``str``
        """
        self.github_6g_sandbox_sites_https_url = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL
        self.github_6g_sandbox_sites_repository_name = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME
        self.github_6g_sandbox_sites_local_directory = os.path.join(tn_folder, self.github_6g_sandbox_sites_repository_name)
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
        self.github_6g_sandbox_sites_commit_id = self.repository_handler.github_commit_id

    def _decrypt_site(self, deployment_site: str) -> None:
        """
        Decrypt core.yaml file of site stored in 6G-Sandbox-Sites repository

        :param deployment_site: trial network deployment site, ``str``
        :raise SixGSandboxSitesDecryptError: if unable to decrypt the core.yaml file from the site (error code 500)
        """
        try:
            password = SixGSandboxSitesSettings.SITES_TOKEN
            secret = password.encode("utf-8")
            vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
            core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, deployment_site, "core.yaml")
            with open(core_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = vault.decrypt(encrypted_data)
            decrypted_yaml = safe_load(decrypted_data)
            decrypted_core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, deployment_site, "core_decrypt.yaml")
            with open(decrypted_core_file, "w") as f:
                safe_dump(decrypted_yaml, f)
        except AnsibleError as e:
            raise SixGSandboxSitesDecryptError(str(e), 500)
        
    def validate_site(self, deployment_site: str) -> None:
        """
        Check if deployment site is valid for deploy trial network
        
        :param deployment_site: trial network deployment site, ``str``
        :return: True if the deployment site is valid. Otherwise False, ``bool``
        """
        if deployment_site not in self.get_sites():
            raise SixGSandboxSitesInvalidSiteError(f"The 'site' should be one: {', '.join(self.get_sites())}", 404)
        self._decrypt_site(deployment_site)
    
    def get_tags(self) -> list[str]:
        """
        Return tags

        :return: list with 6G-Sandbox-Sites tags, ``list[str]``
        """
        return self.repository_handler.get_tags()

    def get_branches(self) -> list[str]:
        """
        Return branches

        :return: list with 6G-Sandbox-Sites branches, ``list[str]``
        """
        return self.repository_handler.get_branches()

    def get_site_available_components(self, deployment_site: str) -> dict:
        """
        Function to get all information of all components available on a site

        :param deployment_site: trial network deployment site, ``str``
        :return: dictionary with all information of all components available on a site, ``dict``
        :raise CustomFileNotFoundError: if core decrypt file not found in site folder (error code 404)
        :raise InvalidContentFileError: if the information in the file is not parsed correctly (error code 422)
        """
        decrypted_core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, deployment_site, "core_decrypt.yaml")
        if not os.path.exists(decrypted_core_file):
            raise CustomFileNotFoundError(f"File '{decrypted_core_file}' not found", 404)
        with open(decrypted_core_file, "rt", encoding="utf8") as f:
            try:
                data = safe_load(f)
            except YAMLError:
                raise InvalidContentFileError(f"File '{decrypted_core_file}' is not parsed correctly", 422)
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
    
    def validate_components_site(self, deployment_site: str, tn_components_types: list[str]) -> None:
        """
        Function to check if components in the descriptor are in the site

        :param deployment_site: trial network deployment site, ``str``
        :param tn_components_types: list of components that compose the descriptor, ``list[str]``
        :raise SixGSandboxSitesComponentsNotFoundError: if the component specified in the descriptor is not in the deployment site (error code 404)
        """
        site_available_components = self.get_site_available_components(deployment_site)
        list_site_available_components = list(site_available_components.keys())
        for component in tn_components_types:
            if component not in list_site_available_components:
                raise SixGSandboxSitesComponentsNotFoundError(f"Component '{component}' entered in descriptor file not found in '{deployment_site}' site", 404)
            log_handler.info(f"Component type '{component}' is on '{deployment_site}' site")