import requests
from collections import OrderedDict

from django.utils.http import urlencode

from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)


class WeixinOAuth2Client(OAuth2Client):

    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            'appid': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope,
            'response_type': 'code'
        }
        if self.state:
            params['state'] = self.state
        params.update(extra_params)
        sorted_params = OrderedDict()
        for param in sorted(params):
            sorted_params[param] = params[param]
        return '%s?%s' % (authorization_url, urlencode(sorted_params))

    def get_access_token(self, code):
        data = {'appid': self.consumer_key,
                'redirect_uri': self.callback_url,
                'grant_type': 'authorization_code',
                'secret': self.consumer_secret,
                'scope': self.scope,
                'code': code}
        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == 'GET':
            params = data
            data = None
        # TODO: Proper exception handling
        resp = requests.request(self.access_token_method,
                                url,
                                params=params,
                                data=data)
        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error('Error retrieving access token: %s'
                              % resp.content)
        return access_token
