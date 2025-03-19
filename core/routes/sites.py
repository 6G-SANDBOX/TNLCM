from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort
from jwt.exceptions import PyJWTError

from core.exceptions.exceptions_handler import CustomException
from core.sites.sites_handler import SitesHandler
from core.utils.os import list_dirs_no_hidden

sites_namespace = Namespace(name="sites", description="Namespace for sites management")


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
            sites_handler.repository_handler.git_clone()
            sites_handler.repository_handler.git_fetch_prune()
            sites_handler.repository_handler.git_checkout()
            sites_handler.repository_handler.git_pull()
            return {"sites": sites_handler.repository_handler.git_branches()}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@sites_namespace.param(
    name="sites_branch", type=str, description="Sites repository branch name"
)
@sites_namespace.route("/<string:sites_branch>")
class BranchDirectories(Resource):
    @sites_namespace.errorhandler(PyJWTError)
    @sites_namespace.errorhandler(JWTExtendedException)
    def get(self, sites_branch: str):
        """
        Retrieve directories from the branch of the sites repository
        """
        try:
            sites_handler = SitesHandler(
                reference_type="branch", reference_value=sites_branch
            )
            sites_handler.repository_handler.git_clone()
            sites_handler.repository_handler.git_fetch_prune()
            sites_handler.repository_handler.git_checkout()
            sites_handler.repository_handler.git_pull()
            return {
                "deployment_sites": list_dirs_no_hidden(
                    path=sites_handler.sites_local_directory
                )
            }, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
