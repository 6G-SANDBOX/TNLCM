from core.models.resource_manager import ResourceManagerModel
from core.exceptions.exceptions_handler import NoResourcesAvailable

class ResourceManagerHandler():

    def __init__(self, trial_network=None, sixg_sandbox_sites_handler=None):
        self.trial_network = trial_network
        self.sixg_sandbox_sites_handler = sixg_sandbox_sites_handler

    def _sixg_sandbox_sites_component_resources(self, component_type):
        """Get component resources from 6G-Sandbox-Sites repository"""
        site_available_components = self.sixg_sandbox_sites_handler.get_site_available_components()
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
        tnlcm_component_resources = ResourceManagerModel.objects(site=self.trial_network.deployment_site, component=component_type).first()
        quantity = 0
        ttl = ""
        if tnlcm_component_resources:
            quantity = tnlcm_component_resources.quantity
            ttl = tnlcm_component_resources.ttl
        return quantity, ttl

    def apply_resource_manager(self):
        """Apply resource manager to check availability resource"""
        tn_descriptor = self.trial_network.json_to_descriptor(self.trial_network.tn_sorted_descriptor)["trial_network"]
        for _, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            sixg_sandbox_sites_component_quantity, sixg_sandbox_sites_component_ttl = self._sixg_sandbox_sites_component_resources(component_type)
            if sixg_sandbox_sites_component_quantity > 0:
                tnlcm_quantity, _ = self._tnlcm_component_resources(component_type)
                if sixg_sandbox_sites_component_quantity == tnlcm_quantity:
                    raise NoResourcesAvailable(f"Component '{component_type}' is not available on the '{self.trial_network.deployment_site}' platform", 400)
                tnlcm_component_resources = ResourceManagerModel.objects(site=self.trial_network.deployment_site, component=component_type).first()
                if not tnlcm_component_resources:
                    tnlcm_component_resources = ResourceManagerModel(site=self.trial_network.deployment_site, component=component_type, quantity=1, ttl=sixg_sandbox_sites_component_ttl)
                else:
                    tnlcm_component_resources.quantity += 1
                tnlcm_component_resources.save()
    
    def release_resource_manager(self):
        """Release resources when destroy or suspend trial network"""
        tn_descriptor = self.trial_network.json_to_descriptor(self.trial_network.tn_sorted_descriptor)["trial_network"]
        for _, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            tnlcm_component_resources = ResourceManagerModel.objects(site=self.trial_network.deployment_site, component=component_type).first()
            tnlcm_component_resources.quantity -= 1
            tnlcm_component_resources.save()