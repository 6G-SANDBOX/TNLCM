from typing import Dict

from mongoengine import Document, IntField, StringField

from core.exceptions.exceptions import ResourceManagerError


class ResourceManagerModel(Document):
    component = StringField(unique=True)
    quantity = IntField()
    tn_id = StringField(max_length=15, unique=True)

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "resource_manager",
        "description": "This collection manages resources",
    }

    def tnlcm_component_resources(self, component_type: str) -> int:
        """
        Return the number of used instances of the component

        :param component_type: type part of the descriptor file, ``str``
        :return: number of used instances of the component, ``int``
        """
        tnlcm_component_resources = ResourceManagerModel.objects(
            component=component_type
        ).first()
        quantity = 0
        if tnlcm_component_resources:
            quantity = tnlcm_component_resources.quantity
        return quantity

    def sites_component_resources(
        self, component_type: str, site_available_components: Dict
    ) -> int:
        """
        Return component resources from Sites repository

        :param component_type: type part of the descriptor file, ``str``
        :param site_available_components: dictionary with all information of all components available on a site, ``Dict``
        :return:
        """
        sites_component_resources = site_available_components[component_type]
        quantity = 0
        if sites_component_resources and "quantity" in sites_component_resources:
            quantity = sites_component_resources["quantity"]
        return quantity

    def apply_resource_manager(
        self, trial_network, site_available_components: Dict
    ) -> None:
        """
        Apply resource manager to check availability resource

        :param trial_network: model of the trial network, ``TrialNetworkModel``
        :param site_available_components: dictionary with all information of all components available on a site, ``Dict``
        :raise ResourceManagerError:
        """
        sorted_descriptor = trial_network.sorted_descriptor["trial_network"]
        for _, entity_data in sorted_descriptor.items():
            component_type = entity_data["type"]
            sites_component_quantity = self.sites_component_resources(
                component_type=component_type,
                site_available_components=site_available_components,
            )
            if sites_component_quantity > 0:
                tnlcm_quantity = self.tnlcm_component_resources(
                    component_type=component_type
                )
                if sites_component_quantity == tnlcm_quantity:
                    raise ResourceManagerError(
                        message=f"Component {component_type} has reached the maximum number of instances",
                        status_code=400,
                    )
                tnlcm_component_resources = ResourceManagerModel.objects(
                    component=component_type
                ).first()
                if not tnlcm_component_resources:
                    tnlcm_component_resources = ResourceManagerModel(
                        component=component_type,
                        tn_id=trial_network.tn_id,
                        quantity=1,
                    )
                else:
                    tnlcm_component_resources.quantity += 1
                tnlcm_component_resources.save()

    def release_resource_manager(self, trial_network) -> None:
        """
        Release resources when destroy or suspend trial network

        :param trial_network: model of the trial network, ``TrialNetworkModel``
        """
        sorted_descriptor = trial_network.sorted_descriptor["trial_network"]
        for _, entity_data in sorted_descriptor.items():
            component_type = entity_data["type"]
            tnlcm_component_resources = ResourceManagerModel.objects(
                component=component_type
            ).first()
            if tnlcm_component_resources and tnlcm_component_resources.quantity > 0:
                tnlcm_component_resources.quantity -= 1
                tnlcm_component_resources.save()
            if tnlcm_component_resources and tnlcm_component_resources.quantity == 0:
                tnlcm_component_resources.delete()

    def to_dict(self) -> Dict:
        return {
            "tn_id": self.tn_id,
            "component": self.component,
            "quantity": self.quantity,
        }

    def __repr__(self) -> str:
        return "<ResourceManager #%s: %s>" % (self.component, self.quantity)
