from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort, reqparse
from jwt.exceptions import PyJWTError

from core.auth.auth import get_current_user_from_jwt
from core.exceptions.exceptions import CustomException
from core.sites.sites_handler import SitesHandler
from core.utils.os import join_path, list_dirs_no_hidden
from core.utils.parser import ansible_decrypt, decode_base64

sites_namespace = Namespace(
    name="sites",
    description="Namespace for sites management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
        }
    },
)


@sites_namespace.route("/branches")
class Branches(Resource):
    def get(self):
        """
        Retrieve branches from the sites repository
        """
        try:
            sites_handler = SitesHandler()
            sites_handler.git_client.clone()
            sites_handler.git_client.reset_hard()
            sites_handler.git_client.fetch_prune()
            sites_handler.git_client.checkout()
            sites_handler.git_client.pull()
            return {"sites": sites_handler.git_client.branches()}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@sites_namespace.param(
    name="branch", type=str, description="Sites repository branch name"
)
@sites_namespace.route("/<string:branch>")
class BranchDirectories(Resource):
    def get(self, branch: str):
        """
        Retrieve directories from the branch of the sites repository
        """
        try:
            sites_handler = SitesHandler(
                reference_type="branch", reference_value=branch
            )
            sites_handler.git_client.clone()
            sites_handler.git_client.reset_hard()
            sites_handler.git_client.fetch_prune()
            sites_handler.git_client.checkout()
            sites_handler.git_client.pull()
            return {
                "deployment_sites": list_dirs_no_hidden(
                    path=sites_handler.sites_local_directory
                )
            }, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@sites_namespace.param(
    name="branch", type=str, description="Sites repository branch name"
)
@sites_namespace.param(
    name="deployment_site", type=str, description="Deployment site directory name"
)
@sites_namespace.route("/<string:branch>/<string:deployment_site>")
class ComponentsAvailable(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument(
        "deployment_site_token",
        type=str,
        required=True,
        help="Deployment site token in base64 to decrypt the core.yaml file",
        location="args",
    )

    @sites_namespace.doc(security="Bearer Auth")
    @sites_namespace.errorhandler(PyJWTError)
    @sites_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @sites_namespace.expect(parser_get)
    def get(self, branch: str, deployment_site: str):
        """
        Retrieve components available in a site
        """
        try:
            deployment_site_token = decode_base64(
                encoded_data=self.parser_get.parse_args()["deployment_site_token"]
            )

            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            if not current_user:
                return {"message": "User not found"}, 404
            sites_handler = SitesHandler(
                reference_type="branch", reference_value=branch
            )
            sites_handler.git_client.clone()
            sites_handler.git_client.reset_hard()
            sites_handler.git_client.fetch_prune()
            sites_handler.git_client.checkout()
            sites_handler.git_client.pull()
            sites_handler.validate_deployment_site(deployment_site=deployment_site)
            ansible_decrypt(
                data_path=join_path(
                    sites_handler.sites_local_directory, deployment_site, "core.yaml"
                ),
                token=deployment_site_token,
            )
            return {
                "components": sites_handler.get_available_components_names(
                    deployment_site=deployment_site
                )
            }, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
