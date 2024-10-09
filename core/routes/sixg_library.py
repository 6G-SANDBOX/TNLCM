from flask_restx import Namespace, Resource, abort, reqparse

from core.sixg_library.sixg_library_handler import SixGLibraryHandler
from core.sixg_sandbox_sites.sixg_sandbox_sites_handler import SixGSandboxSitesHandler
from core.exceptions.exceptions_handler import CustomException

sixg_library_namespace = Namespace(
    name="6G-Library",
    description="Namespace for TNLCM integration with 6G-Library"
)

@sixg_library_namespace.route("/clone")
class Clone(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_post.add_argument("reference_value", type=str, required=True)

    @sixg_library_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Clone 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library.
        """
        try:
            reference_type = self.parser_post.parse_args()["reference_type"]
            reference_value = self.parser_post.parse_args()["reference_value"]
            
            _ = SixGLibraryHandler(reference_type=reference_type, reference_value=reference_value)
            return {"message": "6G-Library cloned"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/name")
class NameComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_sandbox_sites_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_sandbox_sites_reference_value", type=str, required=True)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self) -> tuple[dict, int]:
        """
        Return the components available on a site
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            github_6g_sandbox_sites_reference_type = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_type"]
            github_6g_sandbox_sites_reference_value = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_value"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference_type=github_6g_sandbox_sites_reference_type, reference_value=github_6g_sandbox_sites_reference_value)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            site_available_components = sixg_sandbox_sites_handler.get_site_available_components()
            components_types = list(site_available_components.keys())
            return {
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "components_types": components_types
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/all")
class AllComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_library_reference_value", type=str, required=True)
    parser_get.add_argument("github_6g_sandbox_sites_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_sandbox_sites_reference_value", type=str, required=True)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self) -> tuple[dict, int]:
        """
        Return the metadata, input and output part of components of a site stored in the branch, commit or tag of the 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library.
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            github_6g_library_reference_type = self.parser_get.parse_args()["github_6g_library_reference_type"]
            github_6g_library_reference_value = self.parser_get.parse_args()["github_6g_library_reference_value"]
            github_6g_sandbox_sites_reference_type = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_type"]
            github_6g_sandbox_sites_reference_value = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_value"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference_type=github_6g_sandbox_sites_reference_type, reference_value=github_6g_sandbox_sites_reference_value)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            site_available_components = sixg_sandbox_sites_handler.get_site_available_components()
            components_types = list(site_available_components.keys())
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            all_parts = sixg_library_handler.get_components_parts(site=sixg_sandbox_sites_handler.deployment_site, parts=["input", "metadata", "output"], components_types=components_types)
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "all_parts": all_parts
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/metadata")
class MetadataPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_library_reference_value", type=str, required=True)
    parser_get.add_argument("github_6g_sandbox_sites_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_sandbox_sites_reference_value", type=str, required=True)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self) -> tuple[dict, int]:
        """
        Return the metadata part of the components of a site stored in the branch, commit or tag of the 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library.
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            github_6g_library_reference_type = self.parser_get.parse_args()["github_6g_library_reference_type"]
            github_6g_library_reference_value = self.parser_get.parse_args()["github_6g_library_reference_value"]
            github_6g_sandbox_sites_reference_type = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_type"]
            github_6g_sandbox_sites_reference_value = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_value"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference_type=github_6g_sandbox_sites_reference_type, reference_value=github_6g_sandbox_sites_reference_value)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            site_available_components = sixg_sandbox_sites_handler.get_site_available_components()
            components_types = list(site_available_components.keys())
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            metadata_part = sixg_library_handler.get_components_parts(site=sixg_sandbox_sites_handler.deployment_site, parts=["metadata"], components_types=components_types)
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "part": metadata_part
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/input")
class InputPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_library_reference_value", type=str, required=True)
    parser_get.add_argument("github_6g_sandbox_sites_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_sandbox_sites_reference_value", type=str, required=True)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self) -> tuple[dict, int]:
        """
        Return the input part of the components of a site stored in the branch, commit or tag of the 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library.
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            github_6g_library_reference_type = self.parser_get.parse_args()["github_6g_library_reference_type"]
            github_6g_library_reference_value = self.parser_get.parse_args()["github_6g_library_reference_value"]
            github_6g_sandbox_sites_reference_type = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_type"]
            github_6g_sandbox_sites_reference_value = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_value"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference_type=github_6g_sandbox_sites_reference_type, reference_value=github_6g_sandbox_sites_reference_value)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            site_available_components = sixg_sandbox_sites_handler.get_site_available_components()
            components_types = list(site_available_components.keys())
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            input_part = sixg_library_handler.get_components_parts(site=sixg_sandbox_sites_handler.deployment_site, parts=["input"], components_types=components_types)
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "part": input_part
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/output")
class OutputPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_library_reference_value", type=str, required=True)
    parser_get.add_argument("github_6g_sandbox_sites_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_get.add_argument("github_6g_sandbox_sites_reference_value", type=str, required=True)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self) -> tuple[dict, int]:
        """
        Return the output part of the components of a site stored in the branch, commit or tag of the 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library.
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites.
        """
        try:
            github_6g_library_reference_type = self.parser_get.parse_args()["github_6g_library_reference_type"]
            github_6g_library_reference_value = self.parser_get.parse_args()["github_6g_library_reference_value"]
            github_6g_sandbox_sites_reference_type = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_type"]
            github_6g_sandbox_sites_reference_value = self.parser_get.parse_args()["github_6g_sandbox_sites_reference_value"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference_type=github_6g_sandbox_sites_reference_type, reference_value=github_6g_sandbox_sites_reference_value)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            site_available_components = sixg_sandbox_sites_handler.get_site_available_components()
            components_types = list(site_available_components.keys())
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            output_part = sixg_library_handler.get_components_parts(site=sixg_sandbox_sites_handler.deployment_site, parts=["output"], components_types=components_types)
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "part": output_part
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/tags/")
class Tags(Resource):

    def get(self) -> tuple[dict, int]:
        """
        Return 6G-Library tags
        """
        try:
            sixg_library_handler = SixGLibraryHandler()
            return {"tags": sixg_library_handler.get_tags()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/branches/")
class Branches(Resource):

    def get(self) -> tuple[dict, int]:
        """
        Return 6G-Library branches
        """
        try:
            sixg_library_handler = SixGLibraryHandler()
            return {"branches": sixg_library_handler.get_branches()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))