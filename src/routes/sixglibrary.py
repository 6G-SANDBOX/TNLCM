from flask_restx import Namespace, Resource, abort, reqparse
from git.exc import GitError, GitCommandError, InvalidGitRepositoryError

from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler

sixglibrary_namespace = Namespace(
    name="6G-Library",
    description="TNLCM integration with the 6G-Library"
)

@sixglibrary_namespace.route("/clone/main")
class Clone6GLibrary(Resource):

    def post(self):
        """
        Clone the main branch of the 6G-Library
        """
        try:
            self.sixglibrary_handler = SixGLibraryHandler()
            output = self.sixglibrary_handler.git_clone_6glibrary()
            if output == "cloned":
                if self.sixglibrary_handler.repository_handler.git_branch:
                    return {"message": f"Cloned branch '{self.sixglibrary_handler.repository_handler.git_branch}' in 6G-Library repository"}, 200
                else:
                    return {"message": f"Cloned commit with id '{self.sixglibrary_handler.repository_handler.git_commit_id}' in 6G-Library repository"}, 200
            elif output == "exists":
                return {"message": "6G-Library repository is already cloned"}, 400
            elif output == "updated":
                if self.sixglibrary_handler.repository_handler.git_branch:
                    return {"message": f"Updated to branch '{self.sixglibrary_handler.repository_handler.git_branch}' in 6G-Library repository"}, 200
                else:
                    return {"message": f"Updated to commit with id '{self.sixglibrary_handler.repository_handler.git_commit_id}' in 6G-Library repository"}, 200
            elif output == "updatedpull":
                if self.sixglibrary_handler.repository_handler.git_branch:
                    return {"message": f"Updated to branch '{self.sixglibrary_handler.repository_handler.git_branch}' and pull in 6G-Library repository"}, 200
                else:
                    return {"message": f"Updated to commit with id '{self.sixglibrary_handler.repository_handler.git_commit_id}' and pull in 6G-Library repository"}, 200
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

@sixglibrary_namespace.route("/components/")
class Components6GLibrary(Resource):

    def get(self):
        """
        Returns the components stored in 6G-Library
        """
        try:
            self.sixglibrary_handler = SixGLibraryHandler()
            components = self.sixglibrary_handler.extract_components_6glibrary()
            if components is None:
                return {"messaje": "Clone 6G-Library repository first"}, 400
            else:
                if components:
                    return {"components": components}, 200
                else:
                    return {"message": "No components in 6G-Library"}, 404
        except ValueError as e:
            return abort(400, e)
        except InvalidGitRepositoryError as e:
            return abort(500, e)
        except GitError as e:
            return abort(500, e)
        except Exception as e:
            return abort(422, e)