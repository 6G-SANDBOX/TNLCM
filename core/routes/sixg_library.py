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
    def post(self):
        """
        Clone 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library.
        """
        try:
            reference_type = self.parser_post.parse_args()["reference_type"]
            reference_value = self.parser_post.parse_args()["reference_value"]
            if reference_type == "branch":
                reference_value = f"refs/heads/{reference_value}"
            elif reference_type == "commit":
                reference_value = reference_value
            else:
                reference_value = f"refs/tags/{reference_value}"
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
    def get(self):
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
            return {
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "components": site_available_components
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
    def get(self):
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
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            parts_components = sixg_library_handler.get_parts_components(site=sixg_sandbox_sites_handler.deployment_site, site_available_components=site_available_components)
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "parts_components": parts_components
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
    def get(self):
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
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            parts_components = sixg_library_handler.get_parts_components(site=sixg_sandbox_sites_handler.deployment_site, site_available_components=site_available_components)
            metadata = {component: data["metadata"] for component, data in parts_components.items()}
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "metadata": metadata
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
    def get(self):
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
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            parts_components = sixg_library_handler.get_parts_components(site=sixg_sandbox_sites_handler.deployment_site, site_available_components=site_available_components)
            input = {component: data["input"] for component, data in parts_components.items()}
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "input": input
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
    def get(self):
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
            sixg_library_handler = SixGLibraryHandler(reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value)
            parts_components = sixg_library_handler.get_parts_components(site=sixg_sandbox_sites_handler.deployment_site, site_available_components=site_available_components)
            output = {component: data["output"] for component, data in parts_components.items()}
            return {
                "github_6g_library_commit_id": sixg_library_handler.github_6g_library_commit_id,
                "github_6g_sandbox_sites_commit_id": sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "output": output
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/tags/")
class Tags(Resource):

    def get(self):
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

    def get(self):
        """
        Return 6G-Library branches
        """
        try:
            sixg_library_handler = SixGLibraryHandler()
            return {"branches": sixg_library_handler.get_branches()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))