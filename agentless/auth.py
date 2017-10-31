import os
from urllib.parse import urljoin

from flask import request
from flask_restful import abort
import requests
from requests.exceptions import RequestException

from .app import app


class Session(requests.Session):

    def __init__(self):
        super().__init__()
        self.base_url = os.environ['MICROAUTH_ENDPOINT_URL']
        self.auth = (
            os.environ['MICROAUTH_ACCESS_KEY_ID'],
            os.environ['MICROAUTH_SECRET_ACCESS_KEY'],
        )

    def request(self, method, url, *args, **kwargs):
        return super().request(
            method,
            urljoin(self.base_url, url),
            *args,
            **kwargs
        )


session = Session()


def authorize_with_nothing(action, resource):
    return True


def authorize_with_microauth(action, resource):
    try:
        response = session.post(
            'authorize',
            json={
                'action': action,
                'resource': resource,
                'headers': request.headers.to_list(),
                'context': {},
            },
        )
    except RequestException as e:
        response_json = {
            'Authorized': False,
            'ErrorCode': 'RequestFailed',
            'Message': str(e),
        }
    else:
        print(response.content)
        response_json = response.json()

    if response_json['Authorized'] != True:
        abort(401)

    return response_json


def authorize(action, resource):
    backend_name = app.config.get('AUTHENTICATION_BACKEND', 'microauth')
    backend_fn = globals()[f'authorize_with_{backend_name}']
    return backend_fn(action, resource)
