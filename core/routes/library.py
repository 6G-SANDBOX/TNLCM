from flask_restx import abort, Namespace, Resource
from jwt.exceptions import PyJWTError
from flask_jwt_extended.exceptions import JWTExtendedException

from core.library.library_handler import LibraryHandler, LIBRARY_PATH
from core.utils.os_handler import exists_path
from core.exceptions.exceptions_handler import CustomException

library_namespace = Namespace(
    name="library",
    description="Namespace for library management",
)

@library_namespace.route("/<string:library_reference_type>/<string:library_reference_value>")
class Components(Resource):

    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
    def get(self, library_reference_type: str, library_reference_value: str):
        """
        Retrieve library components
        """
        try:
            library_handler = LibraryHandler(reference_type=library_reference_type, reference_value=library_reference_value, directory_path=LIBRARY_PATH)
            library_handler.git_clone()
            if exists_path(path=library_handler.library_local_directory):
                library_handler.git_pull()
            library_handler.git_checkout()
            components = library_handler.get_components()
            return {"components": components}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@library_namespace.route("/<string:library_reference_type>/<string:library_reference_value>/<string:component_name>")
class Component(Resource):
    
    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
    def get(self, library_reference_type: str, library_reference_value: str, component_name: str):
        """
        Retrieve library component information
        """
        try:
            library_handler = LibraryHandler(reference_type=library_reference_type, reference_value=library_reference_value, directory_path=LIBRARY_PATH)
            library_handler.git_clone()
            if exists_path(path=library_handler.library_local_directory):
                library_handler.git_pull()
                library_handler.git_checkout()
            library_handler.is_component(component_type=component_name)
            component_input = library_handler.get_component_input(component_type=component_name)
            return {"component_input": component_input}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))
