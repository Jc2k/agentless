from agentless import crypto
from agentless.app import db


class PrivateKey(db.Model):

    '''
    An SSH Private Key
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    private_key = db.Column(db.Text())

    @property
    def pkey(self):
        return crypto.load_private_key(self.private_key.encode('utf-8'))

    @property
    def public_key(self):
        """
        Returns the public portion of the key pair in OpenSSH format.

        FIXME: It might be better to de-normalize and have the public key
        unencrypted - this is more of a problem with large numbers of keys
        or keys that are entangled with HSMs.
        """
        foo = crypto.public_key_from_private_key(self.pkey)
        return foo

    def sign(self, data):
        return crypto.ssh_sign_data(self.pkey, data)

    def __repr__(self):
        return f'<PrivateKey {self.name!r}>'
