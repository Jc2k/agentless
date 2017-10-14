from flask import jsonify, request
from flask_restful import Resource, abort, fields, marshal, reqparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from agentless.app import app, api, db
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

    def _get_or_404(self, private_key_id):
        private_key = PrivateKey.query.filter(PrivateKey.id == private_key_id).first()
        if not private_key:
            abort(404, message=f'private_key {private_key_id} does not exist')
        return private_key

    def get(self, private_key_id):
        private_key = self._get_or_404(private_key_id)
        return jsonify(marshal(private_key, private_key_fields))

    def put(self, private_key_id):
        private_key = self._get_or_404(private_key_id)

        args = private_key_parser.parse_args()

        private_key.name = args['name']

        db.session.add(private_key)

        db.session.commit()

        return jsonify(marshal(private_key, private_key_fields))

    def delete(self, private_key_id):
        private_key = self._get_or_404(private_key_id)
        db.session.delete(private_key)

        return '{}', 201


class PrivateKeysResource(Resource):

    def get(self):
        return build_response_for_request(PrivateKey, request, private_key_fields)

    def post(self):
        args = private_key_parser.parse_args()

        key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096, backend=default_backend()
        )

        encoded = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        private_key = PrivateKey(
            name=args['name'],
            private_key=encoded,
        )

        db.session.add(private_key)
        db.session.commit()

        return jsonify(marshal(private_key, private_key_fields))


@app.route('/keys/<key_id>/sign')
def sign_data(key_id):
    private_key = PrivateKey.query.filter(PrivateKey.id == private_key_id).first()
    if not private_key:
        abort(404, message=f'private_key {private_key_id} does not exist')

    parser = reqparse.RequestParser()
    parser.add_argument('data', type=str, location='json', required=True)

    key = serialization.load_der_private_key(
        private_key.private_key,
        password=None,
        backend=default_backend(),
    )

    sig = key.sign(
        args['data'],
        padding=padding.PKCS1v15(),
        algorithm=hashes.SHA1(),
    )

    return jsonify({'signature': sig})


api.add_resource(PrivateKeysResource, '/keys')
api.add_resource(PrivateKeyResource, '/keys/<key_id>')
