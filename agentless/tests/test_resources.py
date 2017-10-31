import base64
import json
import unittest

from agentless.app import app, db
from agentless.models import PrivateKey


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['AUTHENTICATION_BACKEND'] = 'nothing'
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_keys_no_keys(self):
        response = self.client.get('/api/v1/keys')
        assert response.status_code == 200
        assert response.get_data(as_text=True) == '[]\n'
        assert b''.join(response.response) == b'[]\n'

    def test_create_key(self):
        response = self.client.post(
            '/api/v1/keys',
            data='{"name": "my-test-key"}',
            content_type='application/json',
        )
        assert response.status_code == 200

        payload = json.loads(response.get_data(as_text=True))

        assert isinstance(payload, dict)
        assert payload['name'] == 'my-test-key'
        # assert payload['public_key'].startswith('AAA')

    def test_get_keys_1_key(self):
        response = self.client.post(
            '/api/v1/keys',
            data='{"name": "my-test-key"}',
            content_type='application/json',
        )
        assert response.status_code == 200

        response = self.client.get('/api/v1/keys')
        payload = json.loads(response.get_data(as_text=True))

        assert isinstance(payload, list)
        assert len(payload) == 1

        assert payload[0]['name'] == 'my-test-key'
        # assert payload[0]['public_key'].startswith('AAA')

    def test_sign_with_key(self):
        response = self.client.post(
            '/api/v1/keys',
            data='{"name": "my-test-key"}',
            content_type='application/json',
        )
        assert response.status_code == 200
        payload = json.loads(response.get_data(as_text=True))

        data = json.dumps({"data": base64.b64encode(b"hello").decode('utf-8')})

        response = self.client.post(
            f'/api/v1/keys/{payload["id"]}/sign',
            data=data,
            content_type='application/json',
        )
        assert response.status_code == 200
        payload = json.loads(response.get_data(as_text=True))
        assert isinstance(payload, dict)

        signature = base64.b64decode(payload['signature'])
        assert isinstance(signature, bytes)

        private_key = PrivateKey.query.filter(PrivateKey.name == 'my-test-key').first()
        assert signature == private_key.sign(b'hello')
