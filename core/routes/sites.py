from flask_jwt_extended import jwt_required
from flask_restx import abort, Namespace, Resource
from jwt.exceptions import PyJWTError
from flask_jwt_extended.exceptions import JWTExtendedException

from core.sites.sites_handler import SitesHandler
from core.utils.os_handler import current_directory, join_path
from core.exceptions.exceptions_handler import CustomException

sites_namespace = Namespace(
    name="sites",
    description="Namespace for sites management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
)

@sites_namespace.route("/sites/")
class Sites(Resource):

    @sites_namespace.doc(security="Bearer Auth")
    @sites_namespace.errorhandler(PyJWTError)
    @sites_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self):
        """
        Retrieve sites
        """
        try:
            sites_path = join_path(current_directory(), "core", "sites")
            sites_handler = SitesHandler(directory_path=sites_path)
            return {"sites": sites_handler.git_branches()}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))
