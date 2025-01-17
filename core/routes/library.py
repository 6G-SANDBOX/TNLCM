from flask_restx import Namespace, Resource, abort
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

from core.library.library_handler import LibraryHandler
from core.utils.os_handler import current_directory, join_path, exists_path
from core.exceptions.exceptions_handler import CustomException

library_namespace = Namespace(
    name="library",
    description="Namespace for library management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
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
            if not exists_path(path=library_handler.library_local_directory):
                library_handler.git_clone()
            library_handler.is_component(component_type=component)
            component_input = library_handler.get_component_input(component_type=component)
            return {"component_input": component_input}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))