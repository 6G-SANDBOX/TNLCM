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
    parser_post.add_argument("reference", type=str, required=True)

    @sixg_library_namespace.expect(parser_post)
    def post(self):
        """
        Clone 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library. **If nothing is specified, the main branch will be used.**
        """
        try:
            reference = self.parser_post.parse_args()["reference"]

            _ = SixGLibraryHandler(reference=reference)
            return {"message": "6G-Library cloned"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/name")
class NameComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference", type=str, required=False)
    parser_get.add_argument("github_6g_sandbox_sites_reference", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the components of a site stored in the branch or commit of the 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library. **If nothing is specified, the main branch will be used.**
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites. **If nothing is specified, the main branch will be used.**
        """
        try:
            github_6g_library_reference = self.parser_get.parse_args()["github_6g_library_reference"]
            github_6g_sandbox_sites_reference = self.parser_get.parse_args()["github_6g_sandbox_sites_reference"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference=github_6g_sandbox_sites_reference)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            sixg_library_handler = SixGLibraryHandler(reference=github_6g_library_reference, site=sixg_sandbox_sites_handler.deployment_site)
            parts_components = sixg_library_handler.get_parts_components()
            components = list(parts_components.keys())
            return {
                "github_6g_library_reference": sixg_library_handler.github_6g_library_reference,
                "github_6g_sandbox_sites_reference": sixg_sandbox_sites_handler.github_6g_sandbox_sites_reference,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "components": components
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/all")
class AllComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference", type=str, required=False)
    parser_get.add_argument("github_6g_sandbox_sites_reference", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the metadata and input part of components of a site stored in the branch or commit of the 6G-Library repository
        Can specify a branch, commit or tag of the 6G-Library. **If nothing is specified, the main branch will be used.**
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites. **If nothing is specified, the main branch will be used.**
        """
        try:
            github_6g_library_reference = self.parser_get.parse_args()["github_6g_library_reference"]
            github_6g_sandbox_sites_reference = self.parser_get.parse_args()["github_6g_sandbox_sites_reference"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference=github_6g_sandbox_sites_reference)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            sixg_library_handler = SixGLibraryHandler(reference=github_6g_library_reference, site=sixg_sandbox_sites_handler.deployment_site)
            parts_components = sixg_library_handler.get_parts_components()
            return {
                "github_6g_library_reference": sixg_library_handler.github_6g_library_reference,
                "github_6g_sandbox_sites_reference": sixg_sandbox_sites_handler.github_6g_sandbox_sites_reference,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "parts_components": parts_components
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/metadata")
class MetadataPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference", type=str, required=False)
    parser_get.add_argument("github_6g_sandbox_sites_reference", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the metadata part of the components to be specified
        Can specify a branch, commit or tag of the 6G-Library. **If nothing is specified, the main branch will be used.**
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites. **If nothing is specified, the main branch will be used.**
        """
        try:
            github_6g_library_reference = self.parser_get.parse_args()["github_6g_library_reference"]
            github_6g_sandbox_sites_reference = self.parser_get.parse_args()["github_6g_sandbox_sites_reference"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference=github_6g_sandbox_sites_reference)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            sixg_library_handler = SixGLibraryHandler(reference=github_6g_library_reference, site=sixg_sandbox_sites_handler.deployment_site)
            parts_components = sixg_library_handler.get_parts_components()
            metadata = {component: data["metadata"] for component, data in parts_components.items()}
            return {
                "github_6g_library_reference": sixg_library_handler.github_6g_library_reference,
                "github_6g_sandbox_sites_reference": sixg_sandbox_sites_handler.github_6g_sandbox_sites_reference,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "metadata": metadata
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/input")
class InputPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference", type=str, required=False)
    parser_get.add_argument("github_6g_sandbox_sites_reference", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the input part of the components to be specified
        Can specify a branch, commit or tag of the 6G-Library. **If nothing is specified, the main branch will be used.**
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites. **If nothing is specified, the main branch will be used.**
        """
        try:
            github_6g_library_reference = self.parser_get.parse_args()["github_6g_library_reference"]
            github_6g_sandbox_sites_reference = self.parser_get.parse_args()["github_6g_sandbox_sites_reference"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference=github_6g_sandbox_sites_reference)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            sixg_library_handler = SixGLibraryHandler(reference=github_6g_library_reference, site=sixg_sandbox_sites_handler.deployment_site)
            parts_components = sixg_library_handler.get_parts_components()
            input = {component: data["input"] for component, data in parts_components.items()}
            return {
                "github_6g_library_reference": sixg_library_handler.github_6g_library_reference,
                "github_6g_sandbox_sites_reference": sixg_sandbox_sites_handler.github_6g_sandbox_sites_reference,
                "site": sixg_sandbox_sites_handler.deployment_site,
                "input": input
                }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/output")
class OutputPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("github_6g_library_reference", type=str, required=False)
    parser_get.add_argument("github_6g_sandbox_sites_reference", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the output part of the components to be specified
        Can specify a branch, commit or tag of the 6G-Library. **If nothing is specified, the main branch will be used.**
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites. **If nothing is specified, the main branch will be used.**
        """
        try:
            github_6g_library_reference = self.parser_get.parse_args()["github_6g_library_reference"]
            github_6g_sandbox_sites_reference = self.parser_get.parse_args()["github_6g_sandbox_sites_reference"]
            site = self.parser_get.parse_args()["site"]

            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(reference=github_6g_sandbox_sites_reference)
            sixg_sandbox_sites_handler.set_deployment_site(site)
            sixg_library_handler = SixGLibraryHandler(reference=github_6g_library_reference, site=sixg_sandbox_sites_handler.deployment_site)
            parts_components = sixg_library_handler.get_parts_components()
            output = {component: data["output"] for component, data in parts_components.items()}
            return {
                "github_6g_library_reference": sixg_library_handler.github_6g_library_reference,
                "github_6g_sandbox_sites_reference": sixg_sandbox_sites_handler.github_6g_sandbox_sites_reference,
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