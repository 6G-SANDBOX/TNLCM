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
            return {"message": "6G-Library cloned"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/all")
class AllComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)
    parser_get.add_argument("tag", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

    @sixg_library_namespace.expect(parser_get)
    def get(self):
        """
        Return the components of a site stored in the branch or commit_id of the 6G-Library repository
        **Only one of the 3 available fields can be specified: branch, commit_id or tag. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]
            tag = self.parser_get.parse_args()["tag"]
            site = self.parser_get.parse_args()["site"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag, site=site)
            sixg_library_handler.git_clone_6g_library()
            parts_components = sixg_library_handler.get_parts_components()
            components = list(parts_components.keys())
            if branch:
                return {
                    "branch": branch,
                    "site": site,
                    "components": components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "site": site,
                    "components": components
                    }, 200
            elif tag:
                return {
                    "tag": tag,
                    "site": site,
                    "components": components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "site": site,
                    "components": components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/metadata")
class MetadataPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)
    parser_get.add_argument("tag", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

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
            site = self.parser_get.parse_args()["site"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag, site=site)
            sixg_library_handler.git_clone_6g_library()
            parts_components = sixg_library_handler.get_parts_components()
            metadata_part_components = {component: data["metadata"] for component, data in parts_components.items()}
            if branch:
                return {
                    "branch": branch,
                    "site": site,
                    "metadata_part_components": metadata_part_components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "site": site,
                    "metadata_part_components": metadata_part_components
                    }, 200
            elif tag:
                return {
                    "tag": tag,
                    "site": site,
                    "metadata_part_components": metadata_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "site": site,
                    "metadata_part_components": metadata_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixg_library_namespace.route("/components/input")
class InputPartComponents(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)
    parser_get.add_argument("tag", type=str, required=False)
    parser_get.add_argument("site", type=str, required=True)

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
            site = self.parser_get.parse_args()["site"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag, site=site)
            sixg_library_handler.git_clone_6g_library()
            parts_components = sixg_library_handler.get_parts_components()
            input_part_components = {component: data["input"] for component, data in parts_components.items()}
            if branch:
                return {
                    "branch": branch,
                    "site": site,
                    "input_part_components": input_part_components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "site": site,
                    "input_part_components": input_part_components
                    }, 200
            elif tag:
                return {
                    "tag": tag,
                    "site": site,
                    "input_part_components": input_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "site": site,
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
    parser_get.add_argument("site", type=str, required=False)

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
            site = self.parser_get.parse_args()["site"]

            sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id, tag=tag, site=site)
            sixg_library_handler.git_clone_6g_library()
            parts_components = sixg_library_handler.get_parts_components()
            output_part_components = {component: data["output"] for component, data in parts_components.items()}
            if branch:
                return {
                    "branch": branch,
                    "site": site,
                    "output_part_components": output_part_components
                    }, 200
            elif commit_id:
                return {
                    "commit_id": commit_id,
                    "site": site,
                    "output_part_components": output_part_components
                    }, 200
            elif tag:
                return {
                    "tag": tag,
                    "site": site,
                    "output_part_components": output_part_components
                    }, 200
            else:
                return {
                    "branch": sixg_library_handler.github_6g_library_branch,
                    "site": site,
                    "output_part_components": output_part_components
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