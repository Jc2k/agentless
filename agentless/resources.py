import base64

from flask import jsonify, request
from flask_restful import Resource, abort, fields, marshal, reqparse
from flask_tinyauth import authorize_or_401

from agentless import crypto
from agentless.app import api, app, db
from agentless.models import PrivateKey
from agentless.simplerest import build_response_for_request

private_key_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'public_key': fields.String,
}

private_key_parser = reqparse.RequestParser()
private_key_parser.add_argument('name', type=str, location='json', required=True)


class PrivateKeyResource(Resource):

    def _get_or_404(self, key_id):
        private_key = PrivateKey.query.filter(PrivateKey.id == key_id).first()
        if not private_key:
            abort(404, message=f'private_key {key_id} does not exist')
        return private_key

    def get(self, key_id):
        authorize_or_401('GetKey', 'key', key_id)

        private_key = self._get_or_404(key_id)
        return jsonify(marshal(private_key, private_key_fields))

    def put(self, key_id):
        authorize_or_401('UpdateKey', 'key', key_id)

        private_key = self._get_or_404(key_id)

        args = private_key_parser.parse_args()

        private_key.name = args['name']

        db.session.add(private_key)

        db.session.commit()

        return jsonify(marshal(private_key, private_key_fields))

    def delete(self, key_id):
        authorize_or_401('DeleteKey', 'key', key_id)

        private_key = self._get_or_404(key_id)
        db.session.delete(private_key)

        return '{}', 201


class PrivateKeysResource(Resource):

    def get(self):
        authorize_or_401('GetKey', 'key')
        return build_response_for_request(PrivateKey, request, private_key_fields)

    def post(self):
        args = private_key_parser.parse_args()

        authorize_or_401('CreateKey', 'key', args['name'])

        private_key = PrivateKey(
            name=args['name'],
            private_key=crypto.generate_private_key(),
        )

        db.session.add(private_key)
        db.session.commit()

        return jsonify(marshal(private_key, private_key_fields))


@app.route('/api/v1/keys/<string:key_id>/sign', methods=['POST'])
def sign_data(key_id):
    parser = reqparse.RequestParser()
    parser.add_argument('data', type=str, location='json', required=True)
    parser.add_argument('context', type=dict, location='json', required=False)
    args = parser.parse_args()

    authorize_or_401('SignData', 'key', key_id, ctx=args.context)

    private_key = PrivateKey.query.filter(PrivateKey.id == key_id).first()
    if not private_key:
        abort(404, message=f'private_key {key_id} does not exist')

    signature = base64.b64encode(private_key.sign(base64.b64decode(args['data']))).decode('utf-8')

    return jsonify({'signature': signature})


api.add_resource(PrivateKeysResource, '/keys')
api.add_resource(PrivateKeyResource, '/keys/<key_id>')
