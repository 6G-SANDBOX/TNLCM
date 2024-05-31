from flask_restx import Namespace, Resource, abort, reqparse

from core.sixg_sandbox_sites.sixg_sandbox_sites_handler import SixGSandboxSitesHandler
from core.exceptions.exceptions_handler import CustomException

sixg_sandbox_sites_namespace = Namespace(
    name="6G-Sandbox-Sites",
    description="Namespace for TNLCM integration with 6G-Sandbox-Sites"
)

@sixg_sandbox_sites_namespace.route("/clone")
class Clone(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("reference", type=str, required=True)

    @sixg_sandbox_sites_namespace.expect(parser_post)
    def post(self):
        """
        Clone 6G-Sandbox-Sites repository
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites. **If nothing is specified, the main branch will be used.**
        """
        try:
            reference = self.parser_post.parse_args()["reference"]

            _ = SixGSandboxSitesHandler(reference=reference)
            return {"message": "6G-Sandbox-Sites cloned"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/sites")
class Sites(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("reference", type=str, required=True)

    @sixg_sandbox_sites_namespace.expect(parser_get)
    def get(self):
        """
        Return the sites where trial networks can be deployed
        """
        try:
            reference = self.parser_get.parse_args()["reference"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference=reference)
            return {"sites": sixg_sandbox_sites_handler.get_sites()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))