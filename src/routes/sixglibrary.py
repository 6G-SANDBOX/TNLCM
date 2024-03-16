from flask_restx import Namespace, Resource, abort
from git.exc import GitError, GitCommandError

from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler

sixglibrary_namespace = Namespace(
    name="6G-Library",
    description="TNLCM integration with the 6G-Library"
)

@sixglibrary_namespace.route("/clone")
class Clone6GLibrary(Resource):

    def __init__(self, api):
        self.api = api
        self.sixglibrary_handler = SixGLibraryHandler()

    def post(self):
        try:
            self.sixglibrary_handler.git_clone_6glibrary()
            return {"message": "Cloned 6G-Library repository"}, 200
        except GitCommandError as e:
            return abort(404, e)
        except GitError as e:
            return abort(422, e)
        except Exception as e:
            return abort(422, e)

@sixglibrary_namespace.route("/components/")
class Components6GLibrary(Resource):

    def __init__(self, api):
        self.api = api
        self.sixglibrary_handler = SixGLibraryHandler()

    def get(self):
        try:
            components = self.sixglibrary_handler.extract_components_6glibrary()
            return {"components": components}, 200
        except GitCommandError as e:
            return abort(404, e)
        except GitError as e:
            return abort(422, e)
        except Exception as e:
            return abort(422, e)