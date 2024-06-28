from flask_restx import Namespace, Resource, abort
from flask_jwt_extended import jwt_required

from core.jenkins.jenkins_handler import JenkinsHandler
from core.exceptions.exceptions_handler import CustomException

jenkins_namespace = Namespace(
    name="jenkins",
    description="Namespace for handler the jobs in jenkins",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
)

@jenkins_namespace.route("/jobs/")
class Jobs(Resource):

    @jenkins_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return jobs stored in Jenkins
        """
        try:
            jenkins_handler = JenkinsHandler()
            return {"all_jobs": jenkins_handler.get_all_jobs()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))