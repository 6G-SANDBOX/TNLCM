from flask_restx import abort, Namespace, Resource
from jwt.exceptions import PyJWTError
from flask_jwt_extended.exceptions import JWTExtendedException

from core.sites.sites_handler import SitesHandler
from core.utils.os_handler import current_directory, exists_path, join_path, list_directory
from core.exceptions.exceptions_handler import CustomException

sites_namespace = Namespace(
    name="sites",
    description="Namespace for sites management"
)

@sites_namespace.route("/branches/")
class SitesBranches(Resource):

    @sites_namespace.errorhandler(PyJWTError)
    @sites_namespace.errorhandler(JWTExtendedException)
    def get(self):
        """
        Retrieve branches from the Sites repository
        """
        try:
            sites_path = join_path(current_directory(), "core", "sites")
            sites_handler = SitesHandler(directory_path=sites_path)
            sites_handler.git_clone()
            if exists_path(path=sites_handler.sites_local_directory):
                sites_handler.git_pull()
            return {"sites": sites_handler.git_branches()}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@sites_namespace.route("/<string:branch_name>/deployment-sites/")
class SitesBranchDirectories(Resource):

    @sites_namespace.errorhandler(PyJWTError)
    @sites_namespace.errorhandler(JWTExtendedException)
    def get(self, branch_name: str):
        """
        Retrieve directories from the Sites repository
        """
        try:
            sites_path = join_path(current_directory(), "core", "sites")
            sites_handler = SitesHandler(reference_type="branch", reference_value=branch_name, directory_path=sites_path)
            sites_handler.git_clone()
            sites_handler.git_checkout()
            directories = list_directory(path=sites_handler.sites_local_directory)
            # remove directories with .
            directories = [directory for directory in directories if not directory.startswith(".")]
            return {"deployment_sites": directories}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))
