from flask_restx import Namespace, Resource, abort

from core.exceptions.exceptions import CustomException
from core.library.library_handler import LIBRARY_REFERENCES_TYPES, LibraryHandler

library_namespace = Namespace(
    name="library",
    description="Namespace for library management",
)


@library_namespace.route("/references_types")
class ReferencesTypes(Resource):
    def get(self):
        """
        Retrieve library references types
        """
        try:
            return {"library_references_types": LIBRARY_REFERENCES_TYPES}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@library_namespace.param(
    name="reference_type",
    enum=LIBRARY_REFERENCES_TYPES,
)
@library_namespace.route("/<string:reference_type>")
class ReferenceType(Resource):
    def get(self, reference_type: str):
        """
        Retrieve library reference value
        """
        try:
            if reference_type not in LIBRARY_REFERENCES_TYPES:
                return {
                    "message": f"Library reference type {reference_type} is not valid"
                }, 400
            library_handler = LibraryHandler()
            library_handler.git_client.clone()
            library_handler.git_client.fetch_prune()
            library_handler.git_client.checkout()
            library_handler.git_client.pull()
            if reference_type == "branch":
                library_reference_value = library_handler.branches()
            elif reference_type == "tag":
                library_reference_value = library_handler.git_client.tags()
            else:
                library_reference_value = library_handler.git_client.commits()
            return {f"{reference_type}": library_reference_value}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@library_namespace.param(
    name="reference_type",
    enum=LIBRARY_REFERENCES_TYPES,
    description="Library reference type",
)
@library_namespace.param(
    name="reference_value", type="str", description="Library reference value"
)
@library_namespace.route("/<string:reference_type>/<string:reference_value>")
class Components(Resource):
    def get(self, reference_type: str, reference_value: str):
        """
        Retrieve library components
        """
        try:
            library_handler = LibraryHandler()
            library_handler.git_client.clone()
            library_handler.git_client.fetch_prune()
            library_handler.git_client.checkout()
            library_handler.git_client.pull()
            library_handler = LibraryHandler(
                reference_type=reference_type,
                reference_value=reference_value,
            )
            library_handler.git_client.checkout()
            components = library_handler.get_components()
            return {"components": components}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@library_namespace.param(
    name="reference_type",
    enum=LIBRARY_REFERENCES_TYPES,
    description="Library reference type",
)
@library_namespace.param(
    name="reference_value", type="str", description="Library reference value"
)
@library_namespace.param(
    name="component_name", type="str", description="Library component name"
)
@library_namespace.route(
    "/<string:reference_type>/<string:reference_value>/<string:component_name>"
)
class Component(Resource):
    def get(
        self,
        reference_type: str,
        reference_value: str,
        component_name: str,
    ):
        """
        Retrieve library component information
        """
        try:
            library_handler = LibraryHandler()
            library_handler.git_client.clone()
            library_handler.git_client.fetch_prune()
            library_handler.git_client.checkout()
            library_handler.git_client.pull()
            library_handler = LibraryHandler(
                reference_type=reference_type,
                reference_value=reference_value,
            )
            library_handler.git_client.checkout()
            library_handler.is_component_library(component_name=component_name)
            component_input = library_handler.get_component(
                component_name=component_name
            )
            return {"component": component_input}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@library_namespace.param(
    name="reference_type",
    enum=LIBRARY_REFERENCES_TYPES,
    description="Library reference type",
)
@library_namespace.param(
    name="reference_value", type="str", description="Library reference value"
)
@library_namespace.route(
    "/<string:reference_type>/<string:reference_value>/trial-networks-templates"
)
class TrialNetworksTemplates(Resource):
    def get(self, reference_type: str, reference_value: str):
        """
        Retrieve trial networks templates
        """
        try:
            library_handler = LibraryHandler()
            library_handler.git_client.clone()
            library_handler.git_client.fetch_prune()
            library_handler.git_client.checkout()
            library_handler.git_client.pull()
            library_handler = LibraryHandler(
                reference_type=reference_type,
                reference_value=reference_value,
            )
            library_handler.git_client.checkout()
            return {
                "trial_networks_templates": library_handler.get_trial_networks_templates()
            }, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@library_namespace.param(
    name="reference_type",
    enum=LIBRARY_REFERENCES_TYPES,
    description="Library reference type",
)
@library_namespace.param(
    name="reference_value", type="str", description="Library reference value"
)
@library_namespace.param(
    name="component_name", type="str", description="Library component name"
)
@library_namespace.route(
    "/<string:reference_type>/<string:reference_value>/trial-networks-templates/<string:component_name>"
)
class TrialNetworksTemplatesComponent(Resource):
    def get(self, reference_type: str, reference_value: str, component_name: str):
        """
        Retrieve trial networks templates component
        """
        try:
            library_handler = LibraryHandler()
            library_handler.git_client.clone()
            library_handler.git_client.fetch_prune()
            library_handler.git_client.checkout()
            library_handler.git_client.pull()
            library_handler = LibraryHandler(
                reference_type=reference_type,
                reference_value=reference_value,
            )
            library_handler.git_client.checkout()
            library_handler.is_component_library(component_name=component_name)
            trial_networks_templates_component = (
                library_handler.get_trial_networks_templates_component(
                    component_name=component_name
                )
            )
            return {"trial_networks_templates": trial_networks_templates_component}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
