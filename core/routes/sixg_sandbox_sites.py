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
    parser_post.add_argument("branch", type=str, required=False)
    parser_post.add_argument("commit_id", type=str, required=False)
    parser_post.add_argument("tag", type=str, required=False)

    @sixg_sandbox_sites_namespace.expect(parser_post)
    def post(self):
        """
        Clone a branch, commit_id or tag from the 6G-Sandbox-Sites repository
        **Clone the main branch of the default 6G-Sandbox-Sites if no fields are specified**
        **Only one of the 3 available fields can be specified: branch, commit_id or tag**
        """
        try:
            branch = self.parser_post.parse_args()["branch"]
            commit_id = self.parser_post.parse_args()["commit_id"]
            tag = self.parser_post.parse_args()["tag"]

            _ = SixGSandboxSitesHandler(branch=branch, commit_id=commit_id, tag=tag)
            return {"message": "6G-Sandbox-Sites cloned"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/sites")
class Sites(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)
    parser_get.add_argument("tag", type=str, required=False)

    @sixg_sandbox_sites_namespace.expect(parser_get)
    def get(self):
        """
        Return the sites where trial networks can be deployed
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]
            tag = self.parser_get.parse_args()["tag"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(branch=branch, commit_id=commit_id, tag=tag)
            return {"sites": sixg_sandbox_sites_handler.get_sites()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))