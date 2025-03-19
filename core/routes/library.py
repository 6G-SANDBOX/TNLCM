from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort
from jwt.exceptions import PyJWTError

from core.exceptions.exceptions_handler import CustomException
from core.library.library_handler import LIBRARY_REFERENCES_TYPES, LibraryHandler

library_namespace = Namespace(
    name="library",
    description="Namespace for library management",
)


@library_namespace.route("/library_references_types")
class ReferencesTypes(Resource):
    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
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
    name="library_reference_type",
    enum=LIBRARY_REFERENCES_TYPES,
)
@library_namespace.route("/<string:library_reference_type>")
class ReferenceType(Resource):
    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
    def get(self, library_reference_type: str):
        """
        Retrieve library reference value
        """
        try:
            if library_reference_type not in LIBRARY_REFERENCES_TYPES:
                return {
                    "message": f"Library reference type {library_reference_type} is not valid"
                }, 400
            library_handler = LibraryHandler()
            library_handler.repository_handler.git_clone()
            library_handler.repository_handler.git_fetch_prune()
            library_handler.repository_handler.git_checkout()
            library_handler.repository_handler.git_pull()
            if library_reference_type == "branch":
                library_reference_value = library_handler.git_branches()
            elif library_reference_type == "tag":
                library_reference_value = library_handler.repository_handler.git_tags()
            else:
                library_reference_value = (
                    library_handler.repository_handler.git_commits()
                )
            return {f"{library_reference_type}": library_reference_value}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@library_namespace.param(name="library_reference_type", enum=LIBRARY_REFERENCES_TYPES)
@library_namespace.route(
    "/<string:library_reference_type>/<string:library_reference_value>"
)
class Components(Resource):
    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
    def get(self, library_reference_type: str, library_reference_value: str):
        """
        Retrieve library components
        """
        try:
            library_handler = LibraryHandler()
            library_handler.repository_handler.git_clone()
            library_handler.repository_handler.git_fetch_prune()
            library_handler.repository_handler.git_checkout()
            library_handler.repository_handler.git_pull()
            library_handler = LibraryHandler(
                reference_type=library_reference_type,
                reference_value=library_reference_value,
            )
            library_handler.repository_handler.git_checkout()
            components = library_handler.get_components()
            return {"components": components}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@library_namespace.param(name="library_reference_type", enum=LIBRARY_REFERENCES_TYPES)
@library_namespace.route(
    "/<string:library_reference_type>/<string:library_reference_value>/<string:component_name>"
)
class Component(Resource):
    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
    def get(
        self,
        library_reference_type: str,
        library_reference_value: str,
        component_name: str,
    ):
        """
        Retrieve library component information
        """
        try:
            library_handler = LibraryHandler()
            library_handler.repository_handler.git_clone()
            library_handler.repository_handler.git_fetch_prune()
            library_handler.repository_handler.git_checkout()
            library_handler.repository_handler.git_pull()
            library_handler = LibraryHandler(
                reference_type=library_reference_type,
                reference_value=library_reference_value,
            )
            library_handler.repository_handler.git_checkout()
            library_handler.validate_component_available_library(
                component_name=component_name
            )
            component_input = library_handler.get_component_input(
                component_name=component_name
            )
            return {"component_input": component_input}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
