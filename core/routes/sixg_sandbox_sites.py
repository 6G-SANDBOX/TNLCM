from flask_restx import Namespace, Resource, abort, reqparse
from flask_jwt_extended import jwt_required

from core.sixg_sandbox_sites.sixg_sandbox_sites_handler import SixGSandboxSitesHandler
from core.exceptions.exceptions_handler import CustomException

sixg_sandbox_sites_namespace = Namespace(
    name="6G-Sandbox-Sites",
    description="Namespace for TNLCM integration with 6G-Sandbox-Sites",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
)

@sixg_sandbox_sites_namespace.route("/clone")
class Clone(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_post.add_argument("reference_value", type=str, required=True)

    @sixg_sandbox_sites_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @sixg_sandbox_sites_namespace.expect(parser_post)
    def post(self):
        """
        Clone 6G-Sandbox-Sites repository
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            reference_type = self.parser_post.parse_args()["reference_type"]
            reference_value = self.parser_post.parse_args()["reference_value"]
            if reference_type == "branch":
                reference_value = f"refs/heads/{reference_value}"
            elif reference_type == "commit":
                reference_value = reference_value
            elif reference_type == "tag":
                reference_value = f"refs/tags/{reference_value}"
            _ = SixGSandboxSitesHandler(reference_type=reference_type, reference_value=reference_value)
            return {"message": "6G-Sandbox-Sites cloned"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/sites")
class Sites(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("reference", type=str, required=False)

    @sixg_sandbox_sites_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @sixg_sandbox_sites_namespace.expect(parser_get)
    def get(self):
        """
        Return the sites where trial networks can be deployed
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            reference = self.parser_get.parse_args()["reference"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference=reference)
            return {"sites": sixg_sandbox_sites_handler.get_sites()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/tags/")
class Tags(Resource):

    @sixg_sandbox_sites_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return 6G-Sandbox-Sites tags
        """
        try:
            sixg_library_handler = SixGSandboxSitesHandler()
            return {"tags": sixg_library_handler.get_tags()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/branches/")
class Branches(Resource):

    @sixg_sandbox_sites_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return 6G-Sandbox-Sites branches
        """
        try:
            sixg_library_handler = SixGSandboxSitesHandler()
            return {"branches": sixg_library_handler.get_branches()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))