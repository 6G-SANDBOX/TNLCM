from flask_restx import Namespace, Resource, abort, reqparse

from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler
from src.exceptions.exceptions_handler import CustomException

sixglibrary_namespace = Namespace(
    name="6G-Library",
    description="TNLCM integration with the 6G-Library"
)

@sixglibrary_namespace.route("/clone")
class Clone6GLibrary(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("branch", type=str, required=False)
    parser_post.add_argument("commit_id", type=str, required=False)

    @sixglibrary_namespace.expect(parser_post)
    def post(self):
        """
        Clone a branch or commit_id from the 6G-Library
        **Clone the main branch of the default 6G-Library if no fields are specified**
        **If a branch or commit is set that does not exist, the default main branch will be cloned**
        """
        try:
            branch = self.parser_post.parse_args()["branch"]
            commit_id = self.parser_post.parse_args()["commit_id"]

            sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixglibrary_handler.git_clone_6glibrary()
            return {"message": "6G-Library cloned"},  201
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixglibrary_namespace.route("/components/all")
class AllPartsComponents6GLibrary(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixglibrary_namespace.expect(parser_get)
    def get(self):
        """
        Return the components stored in the branch or commit_id of the 6G-Library repository
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixglibrary_handler.git_clone_6glibrary()
            components = sixglibrary_handler.extract_info_components_6glibrary()
            if branch is not None:
                return {
                    "branch": branch, 
                    "components": components
                    }, 200
            elif commit_id is not None:
                return {
                    "commit_id": commit_id, 
                    "components": components
                    }, 200
            else:
                return {
                    "branch": sixglibrary_handler.git_6glibrary_branch, 
                    "components": components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixglibrary_namespace.route("/components/public")
class PublicPartComponents6GLibrary(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixglibrary_namespace.expect(parser_get)
    def get(self):
        """
        Return the public part of the components to be specified
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixglibrary_handler.git_clone_6glibrary()
            components = sixglibrary_handler.extract_components_6glibrary()
            public_part_components = sixglibrary_handler.extract_public_part_component_6glibrary(components)
            if branch is not None:
                return {
                    "branch": branch,
                    "public_part_components": public_part_components
                    }, 200
            elif commit_id is not None:
                return {
                    "commit_id": commit_id, 
                    "public_part_components": public_part_components
                    }, 200
            else:
                return {
                    "branch": sixglibrary_handler.git_6glibrary_branch, 
                    "public_part_components": public_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@sixglibrary_namespace.route("/components/private")
class PrivatePartComponents6GLibrary(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixglibrary_namespace.expect(parser_get)
    def get(self):
        """
        Return the private part of the components to be specified
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixglibrary_handler.git_clone_6glibrary()
            components = sixglibrary_handler.extract_components_6glibrary()
            private_part_components = sixglibrary_handler.extract_private_part_component_6glibrary(components)
            if branch is not None:
                return {
                    "branch": branch,
                    "private_part_components": private_part_components
                    }, 200
            elif commit_id is not None:
                return {
                    "commit_id": commit_id, 
                    "private_part_components": private_part_components
                    }, 200
            else:
                return {
                    "branch": sixglibrary_handler.git_6glibrary_branch, 
                    "private_part_components": private_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        
@sixglibrary_namespace.route("/components/depends")
class DependsPartComponents6GLibrary(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixglibrary_namespace.expect(parser_get)
    def get(self):
        """
        Return the depends part of the components to be specified
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixglibrary_handler.git_clone_6glibrary()
            components = sixglibrary_handler.extract_components_6glibrary()
            depends_part_components = sixglibrary_handler.extract_depends_part_component_6glibrary(components)
            if branch is not None:
                return {
                    "branch": branch,
                    "depends_part_components": depends_part_components
                    }, 200
            elif commit_id is not None:
                return {
                    "commit_id": commit_id, 
                    "depends_part_components": depends_part_components
                    }, 200
            else:
                return {
                    "branch": sixglibrary_handler.git_6glibrary_branch, 
                    "depends_part_components": depends_part_components
                    }, 200
        except CustomException as e:
            return abort(e.error_code, str(e))