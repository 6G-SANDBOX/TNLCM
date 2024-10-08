import os

from yaml import safe_load, YAMLError, safe_dump
from ansible_vault import Vault
from ansible.errors import AnsibleError

from conf import SixGSandboxSitesSettings
from core.logs.log_handler import log_handler
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGSandboxSitesInvalidSiteError, SixGSandboxSitesComponentsNotFoundError, InvalidContentFileError, CustomFileNotFoundError, SixGSandboxSitesDecryptError

SIXG_SANDBOX_SITES_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SixGSandboxSitesHandler():

    def __init__(self, reference_type=None, reference_value=None):
        """
        Constructor
        
        :param reference_type: type of reference (branch, tag, commit) to checkout, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to checkout, ``str``
        """
        self.github_6g_sandbox_sites_https_url = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL
        self.github_6g_sandbox_sites_repository_name = SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME
        self.github_6g_sandbox_sites_local_directory = os.path.join(SIXG_SANDBOX_SITES_DIRECTORY, self.github_6g_sandbox_sites_repository_name)
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
        self.deployment_site = None
        self.repository_handler = RepositoryHandler(github_https_url=self.github_6g_sandbox_sites_https_url, github_repository_name=self.github_6g_sandbox_sites_repository_name, github_local_directory=self.github_6g_sandbox_sites_local_directory, github_reference_type=self.github_6g_sandbox_sites_reference_type, github_reference_value=self.github_6g_sandbox_sites_reference_value)
        self.github_6g_sandbox_sites_commit_id = self.repository_handler.github_commit_id

    def _decrypt_site(self):
        """
        Decrypt core.yaml file of site stored in 6G-Sandbox-Sites repository
        """
        try:
            vault = Vault(SixGSandboxSitesSettings.ANSIBLE_VAULT)
            core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, self.deployment_site, "core.yaml")
            data = vault.load(open(core_file).read())
            decrypted_core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, self.deployment_site, "core_decrypt.yaml")
            with open(decrypted_core_file, "w") as f:
                safe_dump(data, f)
        except AnsibleError as e:
            raise SixGSandboxSitesDecryptError(e, 500)
        
    def set_deployment_site(self, deployment_site):
        """
        Set deployment site to deploy trial network
        
        :param deployment_site: trial network deployment site, ``str``
        """
        if deployment_site not in self.get_sites():
            raise SixGSandboxSitesInvalidSiteError(f"The 'site' should be one: {', '.join(self.get_sites())}", 404)
        self.deployment_site = deployment_site
        self._decrypt_site()
    
    def get_tags(self):
        """
        Return tags
        """
        return self.repository_handler.get_tags()

    def get_branches(self):
        """
        Return branches
        """
        return self.repository_handler.get_branches()

    def get_site_available_components(self):
        """
        Return all information of all components available on a site
        """
        decrypted_core_file = os.path.join(self.github_6g_sandbox_sites_local_directory, self.deployment_site, "core_decrypt.yaml")
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

    def get_sites(self):
        """
        Return sites available to deploy trial networks
        """
        return [site for site in os.listdir(self.github_6g_sandbox_sites_local_directory) if not site.startswith(".") and os.path.isdir(os.path.join(self.github_6g_sandbox_sites_local_directory, site))]
    
    def is_components_site(self, components_types):
        """"
        Return true if components in the descriptor are in the site

        :param components_types: list of components that compose the descriptor , ``list[str]``
        """
        site_available_components = self.get_site_available_components()
        list_site_available_components = list(site_available_components.keys())
        for component in components_types:
            if component not in list_site_available_components:
                raise SixGSandboxSitesComponentsNotFoundError(f"Component '{component}' entered in descriptor file not found in '{self.deployment_site}' site", 404)
            log_handler.info(f"Component type '{component}' is on '{self.deployment_site}' site")
        return True