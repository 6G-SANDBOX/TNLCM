from flask_restx import Namespace, Resource, abort, reqparse
from git.exc import GitError, GitCommandError, InvalidGitRepositoryError

from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler

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
        """
        try:
            branch = self.parser_post.parse_args()["branch"]
            commit_id = self.parser_post.parse_args()["commit_id"]

            sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            output = sixglibrary_handler.git_clone_6glibrary()
            if output == "cloned":
                if sixglibrary_handler.repository_handler.git_branch:
                    return {"message": f"Cloned the '{sixglibrary_handler.repository_handler.git_branch}' branch of 6G-Library repository"}, 200
                else:
                    return {"message": f"Cloned commit id '{sixglibrary_handler.repository_handler.git_commit_id}' from 6G-Library repository"}, 200
            elif output == "exists":
                return {"message": "6G-Library repository is already cloned"}, 400
            elif output == "updated":
                if sixglibrary_handler.repository_handler.git_branch:
                    return {"message": f"Updated to '{sixglibrary_handler.repository_handler.git_branch}' branch in the local 6G-Library repository"}, 200
                else:
                    return {"message": f"Updated to commit id '{sixglibrary_handler.repository_handler.git_commit_id}' the local 6G-Library repository"}, 200
            elif output == "updatedpull":
                if sixglibrary_handler.repository_handler.git_branch:
                    return {"message": f"Updated to '{sixglibrary_handler.repository_handler.git_branch}' branch and pull the local 6G-Library repository"}, 200
                else:
                    return {"message": f"Updated to commit id '{sixglibrary_handler.repository_handler.git_commit_id}' and pull the local 6G-Library repository"}, 200
            else:
                return {"message": "6G-Library repository is cloned, but a git pull has been done"}, 200
        except ValueError as e:
            return abort(400, e)
        except GitCommandError as e:
            return abort(400, e.args[0])
        except InvalidGitRepositoryError as e:
            return abort(500, e)
        except GitError as e:
            return abort(500, e)
        except Exception as e:
            return abort(422, e)

@sixglibrary_namespace.route("/components")
class Components6GLibrary(Resource):

    parser_get = reqparse.RequestParser()
    parser_get.add_argument("branch", type=str, required=False)
    parser_get.add_argument("commit_id", type=str, required=False)

    @sixglibrary_namespace.expect(parser_get)
    def get(self):
        """
        Returns the components stored in the branch or commit_id of the 6G-Library repository
        **Only one of the two values has to be specified. If neither is specified, the main branch will be used**
        """
        try:
            branch = self.parser_get.parse_args()["branch"]
            commit_id = self.parser_get.parse_args()["commit_id"]

            sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
            sixglibrary_handler.git_clone_6glibrary()
            components = sixglibrary_handler.extract_components_6glibrary()
            if components:
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
            else:
                if branch is not None:
                    return {"message": f"No components in the '{branch}' branch of 6G-Library"}, 404
                elif commit_id is not None:
                    return {"message": f"No components in the '{commit_id}' commit of 6G-Library"}, 404
                else:
                    return {"message": f"No components in the '{self.sixglibrary_handler.git_6glibrary_branch}' branch of 6G-Library"}, 404
        except ValueError as e:
            return abort(400, e)
        except InvalidGitRepositoryError as e:
            return abort(500, e)
        except GitError as e:
            return abort(500, e)
        except Exception as e:
            return abort(422, e)