from flask_restx import abort, Namespace, Resource
from jwt.exceptions import PyJWTError
from flask_jwt_extended.exceptions import JWTExtendedException

from core.sites.sites_handler import SitesHandler
from core.utils.os_handler import list_directory
from core.exceptions.exceptions_handler import CustomException

sites_namespace = Namespace(
    name="sites",
    description="Namespace for sites management"
)

@sites_namespace.route("/branches")
class Branches(Resource):

    @sites_namespace.errorhandler(PyJWTError)
    @sites_namespace.errorhandler(JWTExtendedException)
    def get(self):
        """
        Retrieve branches from the sites repository
        """
        try:
            sites_handler = SitesHandler()
            sites_handler.git_clone()
            sites_handler.git_fetch_prune()
            sites_handler.git_checkout()
            sites_handler.git_pull()
            return {"sites": sites_handler.git_branches()}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@sites_namespace.route("/<string:sites_branch>")
class BranchDirectories(Resource):

    @sites_namespace.errorhandler(PyJWTError)
    @sites_namespace.errorhandler(JWTExtendedException)
    def get(self, sites_branch: str):
        """
        Retrieve directories from the branch of the sites repository
        """
        try:
            sites_handler = SitesHandler(reference_type="branch", reference_value=sites_branch)
            sites_handler.git_clone()
            sites_handler.git_fetch_prune()
            sites_handler.git_checkout()
            sites_handler.git_pull()
            directories = list_directory(path=sites_handler.sites_local_directory)
            directories = [directory for directory in directories if not directory.startswith(".")]
            return {"deployment_sites": directories}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))
