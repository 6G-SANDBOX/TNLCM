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
    parser_post.add_argument("tag", type=str, required=False)

    @sixg_library_namespace.expect(parser_post)
    def post(self):
        """
        Clone a branch, commit_id or tag from the 6G-Library repository
        **Clone the main branch of the default 6G-Library if no fields are specified**
        **Only one of the 3 available fields can be specified: branch, commit_id or tag**
        """
        try:
            branch = self.parser_post.parse_args()["branch"]
            commit_id = self.parser_post.parse_args()["commit_id"]
            tag = self.parser_post.parse_args()["tag"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag)
            sixg_library_handler.git_clone_6g_library()
            return {"message": "6G-Library cloned"},  201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/all")
class AllPartsComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)
    parser_get.add_argument("tag", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the components stored in the branch or commit_id of the 6G-Library repository
        **Only one of the 3 available fields can be specified: branch, commit_id or tag. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]
            tag = self.parser_get.parse_args()["tag"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag)
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
            elif tag:
                return {
                    "tag": tag,
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
    parser_get.add_argument("tag", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the input part of the components to be specified
        **Only one of the 3 available fields can be specified: branch, commit_id or tag. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]
            tag = self.parser_get.parse_args()["tag"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag)
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
            elif tag:
                return {
                    "tag": tag,
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
    parser_get.add_argument("tag", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the output part of the components to be specified
        **Only one of the 3 available fields can be specified: branch, commit_id or tag. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]
            tag = self.parser_get.parse_args()["tag"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag)
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
            elif tag:
                return {
                    "tag": tag,
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
    parser_get.add_argument("tag", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the private part of the components to be specified
        **Only one of the 3 available fields can be specified: branch, commit_id or tag. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]
            tag = self.parser_get.parse_args()["tag"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag)
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
            elif tag:
                return {
                    "tag": tag,
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
    parser_get.add_argument("tag", type=str, required=False)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the metadata part of the components to be specified
        **Only one of the 3 available fields can be specified: branch, commit_id or tag. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]
            tag = self.parser_get.parse_args()["tag"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag)
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
            elif tag:
                return {
                    "tag": tag,
                    "metadata_part_components": metadata_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "metadata_part_components": metadata_part_components
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
            sixg_library_handler.git_clone_6g_library()
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
            sixg_library_handler.git_clone_6g_library()
            return {"branches": sixg_library_handler.get_branches()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))