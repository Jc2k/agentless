from agentless.app import db


class PrivateKey(db.Model):

    '''
    An SSH Private Key
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    private_key = db.Column(db.Text())

    def __repr__(self):
        return f'<PrivateKey {self.name!r}>'
