import unittest

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from agentless.crypto import generate_private_key
from agentless.models import PrivateKey


class TestModel(unittest.TestCase):

    def test_public_key(self):
        private_key = PrivateKey(name='my-test-key', private_key=generate_private_key())
        public_key = private_key.public_key
        assert isinstance(public_key, str)
        assert public_key.startswith('ssh-rsa ')

    def test_sign(self):
        private_key = PrivateKey(name='my-test-key', private_key=generate_private_key())
        data = b"hello world"

        signature = private_key.sign(data)

        private_key.pkey.public_key().verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
