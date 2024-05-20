from flask_restx import Namespace, Resource, abort, reqparse

from core.sixg_library.sixg_library_handler import SixGLibraryHandler
from core.exceptions.exceptions_handler import CustomException

sixg_library_namespace = Namespace(
    name="6G-Library",
    description="Namespace for TNLCM integration with 6G-Library"
)

@sixg_library_namespace.route("/clone")
class Clone(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("branch", type=str, required=False)
    parser_post.add_argument("commit_id", type=str, required=False)

    @sixg_library_namespace.expect(parser_post)
    def post(self):
        """
        Clone a branch or commit_id from the 6G-Library repository
        **Clone the main branch of the default 6G-Library if no fields are specified**
        **If a branch or commit is set that does not exist, the default main branch will be cloned**
        """
        try:
            branch = self.parser_post.parse_args()["branch"]
            commit_id = self.parser_post.parse_args()["commit_id"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixg_library_handler.git_clone_6g_library()
            return {"message": "6G-Library cloned"},  201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/all")
class AllPartsComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the components stored in the branch or commit_id of the 6G-Library repository
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixg_library_handler.git_clone_6g_library()
            components = sixg_library_handler.get_parts_components()
            if branch:
                return {
                    "branch": branch,
                    "components": components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "components": components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "components": components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/input")
class InputPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the input part of the components to be specified
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixg_library_handler.git_clone_6g_library()
            components = sixg_library_handler.get_components()
            input_part_components = sixg_library_handler.get_input_part_component(components)
            if branch:
                return {
                    "branch": branch,
                    "input_part_components": input_part_components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "input_part_components": input_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "input_part_components": input_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/output")
class OutputPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the output part of the components to be specified
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixg_library_handler.git_clone_6g_library()
            components = sixg_library_handler.get_components()
            output_part_components = sixg_library_handler.get_output_part_component(components)
            if branch:
                return {
                    "branch": branch,
                    "output_part_components": output_part_components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "output_part_components": output_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "output_part_components": output_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/private")
class PrivatePartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the private part of the components to be specified
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixg_library_handler.git_clone_6g_library()
            components = sixg_library_handler.get_components()
            private_part_components = sixg_library_handler.get_private_part_component(components)
            if branch:
                return {
                    "branch": branch,
                    "private_part_components": private_part_components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "private_part_components": private_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "private_part_components": private_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/metadata")
class MetadataPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the metadata part of the components to be specified
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixg_library_handler.git_clone_6g_library()
            components = sixg_library_handler.get_components()
            metadata_part_components = sixg_library_handler.get_metadata_part_component(components)
            if branch:
                return {
                    "branch": branch,
                    "metadata_part_components": metadata_part_components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "metadata_part_components": metadata_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "metadata_part_components": metadata_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))