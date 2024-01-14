import sys
import os
sys.path.append('..')

from flask import jsonify
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask_restx import Namespace, Resource, reqparse, abort
from json import JSONDecodeError, load

api = Namespace('callback', "Handling the data returned by jenkins after deploying the components")

parser = reqparse.RequestParser()
parser.add_argument('callback', location='files', type=FileStorage, required=True)

callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback')

@api.route("")
class CallbackResource(Resource):
    @api.expect(parser)
    @api.response(200, 'Success')
    @api.response(400, 'Invalid callback format')
    @api.response(422, 'Malformed or insecure callback received')
    def post(self):
        """
        Get jenkins results from deploying components
        """
        arguments = parser.parse_args()
        file: FileStorage = arguments['callback']
        filename = secure_filename(file.filename)
        if '.' in filename and filename.split('.')[-1].lower() in ['json']:
            try:
                callback = load(file.stream)
            except JSONDecodeError as e:
                return abort(422, f"Malformed or insecure callback received: '{e}'.")

            os.makedirs(callback_directory, exist_ok=True)
            file_path = os.path.join(callback_directory, filename)
            file.stream.seek(0)
            file.save(file_path)
            return jsonify({'content': callback, 'savedTo': file_path})
        else:
            return abort(400, "Invalid callback format, only json files will be further processed.")