import sys
sys.path.append('..')

from uuid import UUID
from flask import jsonify
from flask_restx import Namespace, Resource, abort, reqparse
from Library import Library

api = Namespace('playbook', "Component's playbook and 6G-Library handling")


@api.route("/<string:text>")
class TestbedResource(Resource):
    def get(self, text: str):
        Library.UpdateLocalRepository(text)
        return jsonify({'text': text})
