import os

from yaml import safe_load, YAMLError

from conf import SixGSandboxSitesSettings
from core.models.resource_manager import ResourceManagerModel
from core.repository.repository_handler import RepositoryHandler
from core.exceptions.exceptions_handler import SixGSandboxSitesInvalidSiteError, InvalidContentFileError, CustomFileNotFoundError, NoResourcesAvailable

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
        if not values_data or "site_available_components" not in values_data:
            return {}
        site_available_components = values_data["site_available_components"]
        return site_available_components

    def _sixg_sandbox_sites_component_resources(self, component_type):
        """Get component resources from 6G-Sandbox-Sites repository"""
        site_available_components = self.get_site_available_components()
        sixg_sandbox_sites_component_resources = site_available_components[component_type]
        quantity = 0
        ttl = ""
        if sixg_sandbox_sites_component_resources and "quantity" in sixg_sandbox_sites_component_resources:
            quantity = sixg_sandbox_sites_component_resources["quantity"]
        if sixg_sandbox_sites_component_resources and "ttl" in sixg_sandbox_sites_component_resources:
            ttl = sixg_sandbox_sites_component_resources["ttl"]
        return quantity, ttl
    
    def _tnlcm_component_resources(self, component_type):
        """Get component used by TNLCM"""
        tnlcm_component_resources = ResourceManagerModel.objects(site=self.deployment_site, component=component_type).first()
        quantity = 0
        ttl = ""
        if tnlcm_component_resources:
            quantity = tnlcm_component_resources.quantity
            ttl = tnlcm_component_resources.ttl
        return quantity, ttl

    def apply_resource_manager(self, tn_id, tn_sorted_descriptor):
        """Apply resource manager to check availability resource"""
        for _, entity_data in tn_sorted_descriptor.items():
            component_type = entity_data["type"]
            sixg_sandbox_sites_component_quantity, sixg_sandbox_sites_component_ttl = self._sixg_sandbox_sites_component_resources(component_type)
            if sixg_sandbox_sites_component_quantity > 0:
                tnlcm_quantity, _ = self._tnlcm_component_resources(component_type)
                if sixg_sandbox_sites_component_quantity == tnlcm_quantity:
                    raise NoResourcesAvailable(f"Component '{component_type}' is not available on the '{self.deployment_site}' platform", 400)
                tnlcm_component_resources = ResourceManagerModel.objects(site=self.deployment_site, component=component_type).first()
                if not tnlcm_component_resources:
                    tnlcm_component_resources = ResourceManagerModel(site=self.deployment_site, tn_ids=[tn_id], component=component_type, quantity=1, ttl=sixg_sandbox_sites_component_ttl)
                else:
                    tnlcm_component_resources.tn_ids.append(tn_id)
                    tnlcm_component_resources.quantity += 1
                tnlcm_component_resources.save()

    def get_sites(self):
        """Return sites available to deploy trial networks"""
        return os.listdir(os.path.join(self.github_6g_sandbox_sites_local_directory, ".sites"))