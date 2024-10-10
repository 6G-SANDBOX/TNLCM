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
    parser_post.add_argument("reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_post.add_argument("reference_value", type=str, required=True)

    @sixg_sandbox_sites_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Clone 6G-Sandbox-Sites repository
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            reference_type = self.parser_post.parse_args()["reference_type"]
            reference_value = self.parser_post.parse_args()["reference_value"]

            _ = SixGSandboxSitesHandler(reference_type=reference_type, reference_value=reference_value)
            return {"message": "6G-Sandbox-Sites cloned"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/sites")
class Sites(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("reference_value", type=str, required=True)

    @sixg_sandbox_sites_namespace.expect(parser_get)
    def get(self) -> tuple[dict, int]:
        """
        Return the sites where trial networks can be deployed
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            reference_type = self.parser_get.parse_args()["reference_type"]
            reference_value = self.parser_get.parse_args()["reference_value"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference_type=reference_type, reference_value=reference_value)
            return {"sites": sixg_sandbox_sites_handler.get_sites()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/site-available-components")
class ComponentsAvailableSites(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("reference_value", type=str, required=True)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_sandbox_sites_namespace.expect(parser_get)
    def get(self) -> tuple[dict, int]:
        """
        Return the sites where trial networks can be deployed
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            reference_type = self.parser_get.parse_args()["reference_type"]
            reference_value = self.parser_get.parse_args()["reference_value"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference_type=reference_type, reference_value=reference_value)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            site_available_components = sixg_sandbox_sites_handler.get_site_available_components()
            return {"site_available_components": list(site_available_components.keys())}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_sandbox_sites_namespace.route("/tags/")
class Tags(Resource):

    def get(self) -> tuple[dict, int]:
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

    def get(self) -> tuple[dict, int]:
        """
        Return 6G-Sandbox-Sites branches
        """
        try:
            sixg_library_handler = SixGSandboxSitesHandler()
            return {"branches": sixg_library_handler.get_branches()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))