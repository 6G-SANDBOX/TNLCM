from mongoengine import Document, StringField, IntField

from core.exceptions.exceptions_handler import CustomResourceManagerException

class ResourceManagerModel(Document):

    component = StringField(unique=True)
    tn_id = StringField(max_length=15, unique=True)
    quantity = IntField()
    ttl = StringField() # maybe FloatField

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "resource_manager",
        "description": "This collection manages resources"
    }

    def _sixg_sandbox_sites_component_resources(self, component_type: str, site_available_components: dict) -> tuple[int, str]:
        """
        Return component resources from 6G-Sandbox-Sites repository
        
        :param component_type: type part of the descriptor file, ``str``
        :param site_available_components: dictionary with all information of all components available on a site, ``dict``
        :return: tuple containing the quantity (int) and the ttl (str)
        """
        sixg_sandbox_sites_component_resources = site_available_components[component_type]
        quantity = 0
        ttl = ""
        if sixg_sandbox_sites_component_resources and "quantity" in sixg_sandbox_sites_component_resources:
            quantity = sixg_sandbox_sites_component_resources["quantity"]
        if sixg_sandbox_sites_component_resources and "ttl" in sixg_sandbox_sites_component_resources:
            ttl = sixg_sandbox_sites_component_resources["ttl"]
        return quantity, ttl
    
    def _tnlcm_component_resources(self, component_type: str) -> tuple[int, str]:
        """
        Return component information used by TNLCM
        
        :param component_type: type part of the descriptor file, ``str``
        :return: tuple containing the quantity (int) and the ttl (str)
        """
        tnlcm_component_resources = ResourceManagerModel.objects(component=component_type).first()
        quantity = 0
        ttl = ""
        if tnlcm_component_resources:
            quantity = tnlcm_component_resources["quantity"]
            ttl = tnlcm_component_resources["ttl"]
        return quantity, ttl

    def apply_resource_manager(self, trial_network, site_available_components: dict) -> None:
        """
        Apply resource manager to check availability resource

        :param trial_network: model of the trial network, ``TrialNetworkModel``
        :param site_available_components: dictionary with all information of all components available on a site, ``dict``
        :raise CustomResourceManagerException:
        """
        tn_descriptor = trial_network.sorted_descriptor["trial_network"]
        for _, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            sixg_sandbox_sites_component_quantity, sixg_sandbox_sites_component_ttl = self._sixg_sandbox_sites_component_resources(component_type, site_available_components)
            if sixg_sandbox_sites_component_quantity > 0:
                tnlcm_quantity, _ = self._tnlcm_component_resources(component_type)
                if sixg_sandbox_sites_component_quantity == tnlcm_quantity:
                    raise CustomResourceManagerException(f"Component {component_type} is not available on the {trial_network.deployment_site} platform", 400)
                tnlcm_component_resources = ResourceManagerModel.objects(component=component_type).first()
                if not tnlcm_component_resources:
                    tnlcm_component_resources = ResourceManagerModel(component=component_type, tn_id=trial_network.tn_id, quantity=1, ttl=sixg_sandbox_sites_component_ttl)
                else:
                    tnlcm_component_resources.quantity += 1
                tnlcm_component_resources.save()
    
    def release_resource_manager(self, trial_network) -> None:
        """
        Release resources when destroy or suspend trial network

        :param trial_network: model of the trial network, ``TrialNetworkModel``
        """
        tn_descriptor = trial_network.sorted_descriptor["trial_network"]
        for _, entity_data in tn_descriptor.items():
            component_type = entity_data["type"]
            tnlcm_component_resources = ResourceManagerModel.objects(component=component_type).first()
            if tnlcm_component_resources:
                tnlcm_component_resources.quantity -= 1
                if tnlcm_component_resources.quantity == 0:
                    tnlcm_component_resources.delete()
                tnlcm_component_resources.save()
            
    def to_dict(self) -> dict:
        return {
            "tn_id": self.tn_id,
            "component": self.component,
            "quantity": self.quantity,
            "ttl": self.ttl
        }

    def __repr__(self) -> str:
        return "<ResourceManager #%s: %s>" % (self.component, self.quantity)