from flask_restx import abort, Namespace, Resource
from jwt.exceptions import PyJWTError
from flask_jwt_extended.exceptions import JWTExtendedException

from core.library.library_handler import LibraryHandler
from core.utils.os_handler import current_directory, exists_path, join_path
from core.exceptions.exceptions_handler import CustomException

library_namespace = Namespace(
    name="library",
    description="Namespace for library management",
)

@library_namespace.route("/components/<string:component>")
class Component(Resource):
    
    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
    def get(self, component: str):
        """
        Retrieve library component information
        """
        try:
            library_path = join_path(current_directory(), "core", "library")
            library_handler = LibraryHandler(directory_path=library_path)
            library_handler.git_clone()
            if exists_path(path=library_handler.library_local_directory):
                library_handler.git_pull()
            library_handler.is_component(component_type=component)
            component_input = library_handler.get_component_input(component_type=component)
            return {"component_input": component_input}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@library_namespace.route("/components/")
class Components(Resource):

    @library_namespace.errorhandler(PyJWTError)
    @library_namespace.errorhandler(JWTExtendedException)
    def get(self):
        """
        Retrieve library components
        """
        try:
            library_path = join_path(current_directory(), "core", "library")
            library_handler = LibraryHandler(directory_path=library_path)
            library_handler.git_clone()
            if exists_path(path=library_handler.library_local_directory):
                library_handler.git_pull()
            components = library_handler.get_components()
            return {"components": components}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))
