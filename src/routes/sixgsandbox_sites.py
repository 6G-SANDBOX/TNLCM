from flask_restx import Namespace, Resource, abort

from src.sixgsandbox_sites.sixgsandbox_sites_handler import SixGSandboxSitesHandler
from src.exceptions.exceptions_handler import CustomException

sixgsandbox_sites_namespace = Namespace(
    name="6G-Sandbox-Sites",
    description="Namespace for TNLCM integration with 6G-Sandbox-Sites"
)

@sixgsandbox_sites_namespace.route("/clone")
class Clone6GSandboxSites(Resource):

    def post(self):
        """
        Clone 6G-Sandbox-Sites repository
        """
        try:
            sixgsandbox_sites_handler = SixGSandboxSitesHandler()
            sixgsandbox_sites_handler.git_clone_6gsandbox_sites()
            return {"message": "6G-Sandbox-Sites cloned"},  201
        except CustomException as e:
            return abort(e.error_code, str(e))