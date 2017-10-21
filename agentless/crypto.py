from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

backend = default_backend()


def generate_private_key():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=backend,
    )

    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')


def load_private_key(private_key_pem):
    return serialization.load_pem_private_key(
        private_key_pem,
        password=None,
        backend=backend,
    )


def public_key_from_private_key(private_key):
    public_key = private_key.public_key()
    foo = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    ).decode('utf-8')
    return foo

def ssh_sign_data(key, data):
    return key.sign(
        data,
        padding=padding.PKCS1v15(),
        algorithm=hashes.SHA1(),
    )
