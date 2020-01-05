import requests
from time import time
from urllib.parse import parse_qsl

from django.conf import settings
from django.utils.http import urlencode

import jwt

from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)


class Scope(object):
    EMAIL = 'email'
    NAME = 'name'


class AppleOAuth2Client(OAuth2Client):
    """
    Custom client because `Sign In With Apple`:
        * requires `response_mode` field in redirect_url
        * requires special `client_secret` as JWT
    """

    def generate_client_secret(self):
        APPLE_PROVIDER_SETTINGS = getattr(
            settings, 'SOCIALACCOUNT_PROVIDERS', {}
        ).get('apple', {})

        MEMBER_ID = APPLE_PROVIDER_SETTINGS.get('MEMBER_ID', None)
        SECRET_KEY = APPLE_PROVIDER_SETTINGS.get('SECRET_KEY', None)

        CURRENT_TIMESTAMP = int(time())
        claims = {
            'iss': MEMBER_ID,
            'aud': 'https://appleid.apple.com',
            'sub': self.consumer_key,
            'iat': CURRENT_TIMESTAMP,
            'exp': CURRENT_TIMESTAMP + 15777000,
        }
        headers = {'kid': self.consumer_secret, 'alg': 'ES256'}
        client_secret = jwt.encode(
            payload=claims,
            key=SECRET_KEY,
            algorithm='ES256',
            headers=headers
        ).decode('utf-8')
        return client_secret

    def get_access_token(self, code):
        url = self.access_token_url
        client_secret = self.generate_client_secret()
        data = {
            'client_id': self.consumer_key,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.callback_url,
            'client_secret': client_secret
        }
        self._strip_empty_keys(data)
        resp = requests.request(
            self.access_token_method,
            url,
            data=data,
            headers=self.headers)
        access_token = None
        if resp.status_code in [200, 201]:
            if (resp.headers['content-type'].split(
                    ';')[0] == 'application/json' or resp.text[:2] == '{"'):
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.text))
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error('Error retrieving access token: %s'
                              % resp.content)
        return access_token

    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'response_mode': 'form_post',
            'scope': ' '.join([Scope.NAME, Scope.EMAIL]),
            'response_type': 'code'
        }
        if self.state:
            params['state'] = self.state
        params.update(extra_params)
        return '%s?%s' % (authorization_url, urlencode(params))
