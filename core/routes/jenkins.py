# FEATURE: deploy component
# from flask_jwt_extended import get_jwt_identity, jwt_required
# from flask_jwt_extended.exceptions import JWTExtendedException
# from flask_restx import Namespace, Resource, abort
# from jwt.exceptions import PyJWTError

# from core.auth.auth import get_current_user_from_jwt
# from core.exceptions.exceptions_handler import CustomException
# from core.jenkins.jenkins_handler import JenkinsHandler

# jenkins_namespace = Namespace(
#     name="jenkins",
#     description="Namespace for Jenkins management",
#     authorizations={
#         "Bearer Auth": {
#             "type": "apiKey",
#             "in": "header",
#             "name": "Authorization",
#             "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
#         }
#     },
# )


# @jenkins_namespace.route("/component")
# class Component(Resource):
#     parser_post = reqparse.RequestParser()
#     parser_post.add_argument(
#         "tn_id",
#         type=str,
#         required=True,
#         location="form",
#         help="Trial Network Identifier. Valid characters are A-Z, a-z, 0-9 and underscore _. MANDATORY",
#     )
#     parser_post.add_argument(
#         "component_type",
#         type=str,
#         required=True,
#         location="form",
#         help="The type of component being deployed. This component must be developed in the 6G-Library",
#     )
#     parser_post.add_argument(
#         "custom_name",
#         type=str,
#         required=False,
#         location="form",
#         help="Custom name for the component inside the Trial Network. Valid characters are A-Z, a-z, 0-9 and underscore _. MANDATORY except for tn_init (including tn_vxlan and tn_bastion) components",
#     )
#     parser_post.add_argument(
#         "library_url",
#         type=str,
#         required=True,
#         location="form",
#         default=LibrarySettings.LIBRARY_HTTPS_URL,
#         help="6G-Library repository HTTPS URL. Leave it as-is unless you want to test your own fork",
#     )
#     parser_post.add_argument(
#         "library_branch",
#         type=str,
#         required=True,
#         location="form",
#         default=f"refs/heads/{LibrarySettings.LIBRARY_BRANCH}",
#         help="You can specify a branch, commit or tag of the 6G-Library in which your component is developed. Valid inputs: `refs/heads/<branchName>`, `refs/tags/<tagName>` or `<commitId>`",
#     )
#     parser_post.add_argument(
#         "sites_url",
#         type=str,
#         required=True,
#         location="form",
#         default=SitesSettings.SITES_HTTPS_URL,
#         help="6G-Sandbox-Sites repository HTTP URL. Leave it as-is unless you want to test your own fork",
#     )
#     parser_post.add_argument(
#         "sites_branch",
#         type=str,
#         required=True,
#         location="form",
#         default=f"refs/heads/{SitesSettings.SITES_BRANCH}",
#         help="You can specify a branch, commit or tag of 6G-Sandbox-Sites with your platform. Valid inputs: `refs/heads/<branchName>`, `refs/tags/<tagName>` or `<commitId>`",
#     )
#     parser_post.add_argument(
#         "deployment_site",
#         type=str,
#         required=True,
#         location="form",
#         help="The site where the component is to be deployed. It must be a directory inside the branch of the Sites repository",
#     )
#     parser_post.add_argument(
#         "debug",
#         type=str,
#         required=True,
#         location="form",
#         choices=["True", "False"],
#         help="Flag for debugging your component",
#     )
#     parser_post.add_argument(
#         "file",
#         location="files",
#         type=FileStorage,
#         required=True,
#         help="YAML file in which you must specify the mandatory fields from the input section of the public.yaml file of the component in the 6G-Library",
#     )

#     @jenkins_namespace.doc(security="Bearer Auth")
#     @jenkins_namespace.errorhandler(PyJWTError)
#     @jenkins_namespace.errorhandler(JWTExtendedException)
#     @jwt_required()
#     @jenkins_namespace.expect(parser_post)
#     def post(self):
#         """
#         Trigger pipeline to deploy a component
#         """
#         try:
#             tn_id = self.parser_post.parse_args()["tn_id"]
#             component_type = self.parser_post.parse_args()["component_type"]
#             custom_name = self.parser_post.parse_args()["custom_name"]
#             deployment_site = self.parser_post.parse_args()["deployment_site"]
#             library_url = self.parser_post.parse_args()["library_url"]
#             library_branch = self.parser_post.parse_args()["library_branch"]
#             sites_url = self.parser_post.parse_args()["sites_url"]
#             sites_branch = self.parser_post.parse_args()["sites_branch"]
#             debug = self.parser_post.parse_args()["debug"]
#             file = self.parser_post.parse_args()["file"]

#             current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
#             trial_network = TrialNetworkModel.objects(
#                 user_created=current_user.username, tn_id=tn_id
#             ).first()
#             if current_user.role == "admin":
#                 trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
#             if trial_network:
#                 return {
#                     "message": f"Trial network with identifier {tn_id} already exists"
#                 }, 400
#             make_directory(join_path(TRIAL_NETWORKS_DIRECTORY_PATH, tn_id))
#             if debug == "True":
#                 debug = True
#             else:
#                 debug = False
#             build_params = {
#                 "TN_ID": tn_id,
#                 "COMPONENT_TYPE": component_type,
#                 "DEPLOYMENT_SITE": deployment_site,
#                 "TNLCM_CALLBACK": TnlcmSettings.TNLCM_CALLBACK,
#                 "LIBRARY_URL": library_url,
#                 "LIBRARY_BRANCH": library_branch,
#                 "SITES_URL": sites_url,
#                 "SITES_BRANCH": sites_branch,
#                 "DEBUG": debug,
#             }
#             if custom_name:
#                 build_params["CUSTOM_NAME"] = custom_name
#             jenkins_handler = JenkinsHandler()
#             pipeline_name, _ = jenkins_handler.clone_pipeline(
#                 old_name=JenkinsSettings.JENKINS_DEPLOY_PIPELINE,
#                 new_name=JenkinsSettings.JENKINS_TNLCM_DIRECTORY
#                 + "/"
#                 + JenkinsSettings.JENKINS_DEPLOY_PIPELINE
#                 + "_"
#                 + tn_id,
#             )
#             jenkins_handler.deploy_component(
#                 tn_id=tn_id,
#                 pipeline_name=pipeline_name,
#                 build_params=build_params,
#                 file=file,
#             )
#             return {
#                 "message": f"Pipeline {pipeline_name} triggered to deploy component {component_type} in trial network {tn_id}"
#             }, 201
#         except CustomException as e:
#             return {"message": str(e.message)}, e.status_code
#         except Exception as e:
#             return abort(code=500, message=str(e))

#     parser_delete = reqparse.RequestParser()
#     parser_delete.add_argument(
#         "tn_id",
#         type=str,
#         required=True,
#         location="form",
#         help="Trial Network Identifier. Valid characters are A-Z, a-z, 0-9 and underscore _. MANDATORY",
#     )
#     parser_delete.add_argument(
#         "library_url",
#         type=str,
#         required=True,
#         location="form",
#         default=LibrarySettings.LIBRARY_HTTPS_URL,
#         help="6G-Library repository HTTPS URL. Leave it as-is unless you want to test your own fork",
#     )
#     parser_delete.add_argument(
#         "library_branch",
#         type=str,
#         required=True,
#         location="form",
#         default=f"refs/heads/{LibrarySettings.LIBRARY_BRANCH}",
#         help="You can specify a branch, commit or tag of the 6G-Library in which your component is developed. Valid inputs: `refs/heads/<branchName>`, `refs/tags/<tagName>` or `<commitId>`",
#     )
#     parser_delete.add_argument(
#         "sites_url",
#         type=str,
#         required=True,
#         location="form",
#         default=SitesSettings.SITES_HTTPS_URL,
#         help="6G-Sandbox-Sites repository HTTP URL. Leave it as-is unless you want to test your own fork",
#     )
#     parser_delete.add_argument(
#         "sites_branch",
#         type=str,
#         required=True,
#         location="form",
#         default=f"refs/heads/{SitesSettings.SITES_BRANCH}",
#         help="You can specify a branch, commit or tag of 6G-Sandbox-Sites with your platform. Valid inputs: `refs/heads/<branchName>`, `refs/tags/<tagName>` or `<commitId>`",
#     )
#     parser_delete.add_argument(
#         "deployment_site",
#         type=str,
#         required=True,
#         location="form",
#         help="The site where the component is to be deployed. It must be a directory inside the branch of the Sites repository",
#     )
#     parser_delete.add_argument(
#         "debug",
#         type=str,
#         required=True,
#         location="form",
#         choices=["True", "False"],
#         help="Flag for debugging your component",
#     )

#     @jenkins_namespace.doc(security="Bearer Auth")
#     @jenkins_namespace.errorhandler(PyJWTError)
#     @jenkins_namespace.errorhandler(JWTExtendedException)
#     @jwt_required()
#     @jenkins_namespace.expect(parser_delete)
#     def delete(self):
#         """
#         Trigger pipeline to destroy a component
#         """
#         try:
#             tn_id = self.parser_post.parse_args()["tn_id"]
#             deployment_site = self.parser_post.parse_args()["deployment_site"]
#             library_url = self.parser_post.parse_args()["library_url"]
#             library_branch = self.parser_post.parse_args()["library_branch"]
#             sites_url = self.parser_post.parse_args()["sites_url"]
#             sites_branch = self.parser_post.parse_args()["sites_branch"]
#             debug = self.parser_post.parse_args()["debug"]

#             current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
#             trial_network = TrialNetworkModel.objects(
#                 user_created=current_user.username, tn_id=tn_id
#             ).first()
#             if current_user.role == "admin":
#                 trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
#             if trial_network:
#                 return {
#                     "message": f"Trial network with identifier {tn_id} already exists"
#                 }, 400
#             make_directory(join_path(TRIAL_NETWORKS_DIRECTORY_PATH, tn_id))
#             if debug == "True":
#                 debug = True
#             else:
#                 debug = False
#             build_params = {
#                 "TN_ID": tn_id,
#                 "DEPLOYMENT_SITE": deployment_site,
#                 "TNLCM_CALLBACK": TnlcmSettings.TNLCM_CALLBACK,
#                 "LIBRARY_URL": library_url,
#                 "LIBRARY_BRANCH": library_branch,
#                 "SITES_URL": sites_url,
#                 "SITES_BRANCH": sites_branch,
#                 "DEBUG": debug,
#             }
#             jenkins_handler = JenkinsHandler()
#             pipeline_name, _ = jenkins_handler.clone_pipeline(
#                 old_name=JenkinsSettings.JENKINS_DEPLOY_PIPELINE,
#                 new_name=JenkinsSettings.JENKINS_TNLCM_DIRECTORY
#                 + "/"
#                 + JenkinsSettings.JENKINS_DEPLOY_PIPELINE
#                 + "_"
#                 + tn_id,
#             )
#             jenkins_handler.destroy_component(
#                 tn_id=tn_id,
#                 pipeline_name=pipeline_name,
#                 build_params=build_params,
#             )
#             return {
#                 "message": f"Pipeline {pipeline_name} triggered to destroy trial network {tn_id}"
#             }, 200
#         except CustomException as e:
#             return {"message": str(e.message)}, e.status_code
#         except Exception as e:
#             return abort(code=500, message=str(e))


# @jenkins_namespace.route("/pipelines")
# class Pipelines(Resource):
#     @jenkins_namespace.doc(security="Bearer Auth")
#     @jenkins_namespace.errorhandler(PyJWTError)
#     @jenkins_namespace.errorhandler(JWTExtendedException)
#     @jwt_required()
#     def get(self):
#         """
#         Retrieve pipelines stored in Jenkins
#         """
#         try:
#             _ = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
#             jenkins_handler = JenkinsHandler()
#             return {"pipelines": jenkins_handler.get_all_pipelines()}, 200
#         except CustomException as e:
#             return {"message": str(e.message)}, e.status_code
#         except Exception as e:
#             return abort(code=500, message=str(e))


# @jenkins_namespace.param(
#     name="pipeline_name", type="str", description="The name of the pipeline to remove"
# )
# @jenkins_namespace.route("/pipelines/<string:pipeline_name>")
# class RemovePipeline(Resource):
#     @jenkins_namespace.doc(security="Bearer Auth")
#     @jenkins_namespace.errorhandler(PyJWTError)
#     @jenkins_namespace.errorhandler(JWTExtendedException)
#     @jwt_required()
#     def delete(self, pipeline_name: str):
#         """
#         Remove a pipeline stored in Jenkins
#         """
#         try:
#             _ = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
#             jenkins_handler = JenkinsHandler()
#             jenkins_handler.remove_pipeline(pipeline_name=pipeline_name)
#             return {"message": f"Pipeline {pipeline_name} successfully removed"}, 200
#         except CustomException as e:
#             return {"message": str(e.message)}, e.status_code
#         except Exception as e:
#             return abort(code=500, message=str(e))
