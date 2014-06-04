from __future__ import absolute_import

import re, requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class OpenidConnectClient(OAuth2Client):

    def __init__(self, request, consumer_key, consumer_secret,
                 access_token_method,
                 access_token_url,
                 callback_url,
                 open_id_url,
                 scope):
        self.request = request
        self.access_token_method = access_token_method
        self.access_token_url = access_token_url
        self.open_id_url = open_id_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope = ' '.join(scope)
        self.state = None

    def get_open_id(self, token):
        params = {'access_token': token}
        resp = requests.request('GET',
                                url = self.open_id_url,
                                params=params)
        open_id = None
        if resp.status_code == 200:
                respContent = str(resp.content, encoding="UTF-8")
                open_id = re.search(r'openid":"([A-F0-9]+)"', respContent).groups()[0]
        if not open_id:
            raise OAuth2Error('Error retrieving open id: %s'
                              % resp.content)
        return open_id
