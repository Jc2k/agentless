import os
from flask import request
from flask_restful import abort
import requests
from requests.exceptions import RequestException

from .app import app


def authorize_with_nothing(action, resource):
    return True


def authorize_with_microauth(action, resource):
    try:
        response = requests.post(
            'http://microauth:5000/api/v1/authorize',
            auth=(os.environ['MICROAUTH_ACCESS_KEY_ID'], os.environ['MICROAUTH_SECRET_ACCESS_KEY']),
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
