import sys
sys.path.append('..')
from Testbed import Testbed  # Otherwise this will use different class variables from app

from flask import jsonify
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask_restx import Namespace, Resource, reqparse, abort
from yaml import safe_load, YAMLError


api = Namespace('testbed', "Testbed status and management")

parser = reqparse.RequestParser()
parser.add_argument('descriptor', location='files', type=FileStorage, required=True)

@api.route("/")
class TestbedResource(Resource):
    def get(self):
        return jsonify({'trial_networks': Testbed.ListTrialNetworks()})

    @api.expect(parser)
    @api.response(200, 'Success')
    @api.response(400, 'Invalid descriptor format')
    @api.response(422, 'Malformed or insecure descriptor received')
    def post(self):
        arguments = parser.parse_args()
        file: FileStorage = arguments['descriptor']
        filename = secure_filename(file.filename)
        if '.' in filename and filename.split('.')[-1].lower() in ['yml', 'yaml']:
            try:
                descriptor = safe_load(file.stream)
            except YAMLError as e:
                return abort(422, f"Malformed or insecure descriptor received: '{e}'.")

            tn = Testbed.CreateAndAddTrialNetwork(descriptor)
            return jsonify({'id': tn.Id})
        else:
            return abort(400, "Invalid descriptor format, only 'yml' or 'yaml' files will be further processed.")
